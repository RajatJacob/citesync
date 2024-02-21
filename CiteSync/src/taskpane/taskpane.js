/* global document, Office, Word */

Office.onReady((info) => {
  if (info.host === Office.HostType.Word) {
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    document.getElementById("run").onclick = run;
  }
});

function addError(error) {
  document.getElementById('error').innerText+=`\n${error}`;
  document.getElementById('run').innerText = "Run";
}

function setRunning() {
  document.getElementById('error').innerText = "";
  document.getElementById("run").innerText = "Running...";
  document.getElementById('run').classList.add('running');
}

function setSuccess() {
  document.getElementById('error').innerText = "";
  document.getElementById('run').innerText = "Run";
  document.getElementById('run').classList.remove('running');
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
      url.searchParams.set('q', highlightedText);
      const response = await fetch(url.toString());

      if (response.ok) {
        setSuccess();
        const citation = JSON.stringify(await response.json());
        const paragraph = context.document.body.insertParagraph(citation, Word.InsertLocation.end);
        paragraph.font.color = "blue";
      }else {
        addError("Oh no! Something's not OK");
      }
    } catch (e) {
      addError(e);
    }
    await context.sync();
  });
}
