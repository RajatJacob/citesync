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

      // Insert a paragraph at the end of the document with the selected text
      const paragraph = context.document.body.insertParagraph(range.text, Word.InsertLocation.end);

      // Change the paragraph color to blue.
      paragraph.font.color = "blue";

      // Synchronize again to apply the changes
      await context.sync();
  });
}

