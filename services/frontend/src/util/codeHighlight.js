import { codeAnalyzer } from "../util/codeAnalyzer.js"
import { db } from "../util/dbInterface.js"

export const highlighter = {
    highlightCode(modelComponent) {
        codeAnalyzer.analyze(modelComponent.generatedPrediction.id)
        .then((responseJson) => {
            const codeSnippetIds = responseJson.code_snippets;
            let promises = [];
            for (const codeSnippetId of codeSnippetIds) {

                promises.push(db.getById("code_snippets", codeSnippetId));
            }
            Promise.all(promises)
            .then((codeSnippets) => {
                const sortedCodeSnippets = codeSnippets.sort((a, b) => a.start_line - b.start_line);
                const codeSnippetCount = sortedCodeSnippets.length;
                const lines = modelComponent.generatedPrediction.text.split("\n");
                const lineCount = lines.length;
                let resultChunks = [];
                let currentCodeSnippetIndex = 0;
                for (let line = 0; line < lineCount; ++line) {
                    if (currentCodeSnippetIndex < codeSnippetCount)  {
                        if (line == sortedCodeSnippets[currentCodeSnippetIndex].start_line) {
                            resultChunks.push({
                                type: "code",
                                codeSnippet: sortedCodeSnippets[currentCodeSnippetIndex],
                                clickableNames: modelComponent.clickableNames
                            });
                            line = sortedCodeSnippets[currentCodeSnippetIndex].end_line;
                            ++currentCodeSnippetIndex;
                            continue;
                        }
                    }
                    if (lines[line].startsWith("```")) continue;
                    resultChunks.push({
                        type: "text",
                        content: lines[line]
                    });
                }
                modelComponent.resultChunks = resultChunks;
                modelComponent.highlighted = true;
            });
        })
        .catch((error) => {
            console.log(error);
        });
    }
}
