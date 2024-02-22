/* global document, Office, Word */

const isDev = true;

function addError(error) {
  if(!isDev) return;
  document.getElementById("error").innerText += `\n${error}`;
  document.getElementById("run").innerText = "Run";
}

function setRunning() {
  document.getElementById("error").innerText = "";
  document.getElementById("run").innerText = "Running...";
  document.getElementById("run").classList.add("running");
}

function setSuccess() {
  document.getElementById("error").innerText = "";
  document.getElementById("run").innerText = "Run";
  document.getElementById("run").classList.remove("running");
}


Office.onReady((info) => {
  if (info.host === Office.HostType.Word) {
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    document.getElementById("run").onclick = run;
  }
  document.global = {
    citations: {
      list: [],
    },
  };
  Word.run(async (context) => {
    const bibliography = context.document.body.insertParagraph("", Word.InsertLocation.end);
    bibliography.load('uniqueLocalId');
    await context.sync();
    const heading = bibliography.insertText("Bibliography", Word.InsertLocation.end);
    heading.font.size = 16;
    heading.font.bold = true;
    document.global.bibliographyId = bibliography.uniqueLocalId;
    return context.sync();
  }).catch(e => {
    addError("INIT: " + JSON.stringify(e));
  })
});

async function addCitation(ama, context) {
  if (!document.global.citations.list.includes(ama)) {
    document.global.citations.list.push(ama);
    const i = document.global.citations.list.indexOf(ama)
    const bibliography = context.document.getParagraphByUniqueLocalId(document.global.bibliographyId);
    bibliography.load('uniqueLocalId, lists');
    await context.sync();
    const citationPara = bibliography.insertParagraph(`[${i+1}] ${ama}`, Word.InsertLocation.after);
    if(i===0) citationPara.startNewList();
    citationPara.font.size = 14;
    citationPara.font.bold = false;
    citationPara.load('uniqueLocalId');
    await context.sync();
    document.global.bibliographyId = citationPara.uniqueLocalId;
  }
  return document.global.citations.list.indexOf(ama);
}

export async function run() {
  setRunning();
  return Word.run(async (context) => {
    const range = context.document.getSelection();
    range.load("text");
    await context.sync();

    const highlightedText = range.text.replace("\r", "");
    try {
      const url = new URL("https://citesync.rajatjacob.com/ama");
      url.searchParams.set("q", highlightedText);
      const response = await fetch(url.toString());

      if (response.ok) {
        setSuccess();
        const citation = JSON.stringify(await response.json());
        const i = await addCitation(citation, context);
        const citationText = range.insertText(` [${i+1}]`, Word.InsertLocation.end);
        citationText.font.superscript = true;
        citationText.font.color = "blue";
      } else {
        addError("CITATION: Oh no! Something's not OK");
      }
    } catch (e) {
      addError("TRY: "+e+" "+JSON.stringify(e));
    }
    await context.sync();
  });
}
