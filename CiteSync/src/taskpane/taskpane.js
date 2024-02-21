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
  console.log("RUNNNNNNN")
  return Word.run(async (context) => {
      // Get the currently selected text
      const range = context.document.getSelection();
      range.load("text");
      console.log("SELECTED TEXT", range.text);

      // Synchronize to execute the load operation
      await context.sync();

      // Extract the highlighted word
      const highlightedWord = range.text.replace('\r', '');

      // Make an HTTP POST request to your Flask backend
      const response = await fetch('http://127.0.0.1:5000/ama', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: highlightedWord })
      });

      // Check if the request was successful
      if (response.ok) {
        // Get the response text
        const output = await response.text();
        console.log("RECEIVED", output);
        
        // Insert the output into the Word document
        const paragraph = context.document.body.insertParagraph(output, Word.InsertLocation.end);
        paragraph.font.color = "blue"; // Change the font color to blue

        // Synchronize to apply the changes
        await context.sync();
      } else {
        console.error('Error:', response.statusText);
      }
  });
}

