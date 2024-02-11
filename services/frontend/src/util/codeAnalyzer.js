import { host } from "../util/util.js";

const codeAnalyzerPort = 5002;

export const codeAnalyzer = {
    analyze(predictionId) {
        return fetch(`http://${host()}:${codeAnalyzerPort}/analyze-prediction?prediction=${predictionId}`)
        .then(response => response.json())
        .catch(error => console.log(error));
    },

    highlight(codeSnippetId, clickableClass, clickableNames, onClickAttribute, clickHandler) {
        return fetch(`http://${host()}:${codeAnalyzerPort}/highlight?code_snippet=${codeSnippetId}&clickable_class=${clickableClass}&clickable_names=${clickableNames}&on_click_attribute=${onClickAttribute}&click_handler=${clickHandler}`)
        .then(response => response.json())
        .catch(error => console.log(error));
    }
};
