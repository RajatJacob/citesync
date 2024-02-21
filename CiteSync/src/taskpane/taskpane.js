/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global document, Office, Word */

Office.onReady((info) => {
  if (info.host === Office.HostType.Word) {
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    document.getElementById("run").onclick = run;
  }
});
export async function run() {
  return Word.run(async (context) => {
    // Get the currently selected text
    const range = context.document.getSelection();
    range.load("text");

    // Synchronize to execute the load operation
    await context.sync();

    const highlightedText = range.text.replace("\r", "");
    document.getElementById("run").innerText = "Running...";
    try {
      document.getElementById("error").innerText += "STARTING\n"
      // const response = await fetch('https://jsonplaceholder.typicode.com/todos/1')
      const response = await fetch("http://127.0.0.1:5000/ama", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: highlightedText }),
      });
      document.getElementById("error").innerText += "REQUEST DONE\n"

      if (response.ok) {
        document.getElementById("error").innerText += "OK\n"
        const citation = JSON.stringify(await response.json());
        document.getElementById("error").innerText += "JSON\n"+citation
        const paragraph = context.document.body.insertParagraph(citation, Word.InsertLocation.end);
        paragraph.font.color = "blue";
      }else {
        document.getElementById("error").innerText += "NOT OK\n"
        console.error("NOT OK")
      }
    } catch (e) {
      console.error(e);
      document.getElementById("error").innerText = "Error!\n" + e;
    }
    document.getElementById("run").innerText = "Ran";
    await context.sync();
  });
}
