import { host } from "./util";

const llmPort = 5001;

function assembleUrl(
    llmId,
    promptPartIds,
    frameworkItemId,
    options,
    stream
) {
    let url = `http://${host()}:${llmPort}/generate?model=${llmId}&prompt_parts=${promptPartIds.toString()}&framework_item=${frameworkItemId}`;
    if (options) {
        if (options.maxTokens) url += `&max_tokens=${options.maxTokens}`;
        if (options.stopSequences) url += `&stop_sequences=${options.stopSequences.toString()}`;
        if (options.temperature) url += `&temperature=${options.temperature}`;
        if (options.parentFollowUpId) url += `&parent_follow_up=${options.parentFollowUpId}`;
    }
    if (stream) url += "&stream=true";
    return url;
}

export const llm = {
    generateNoStream(llmId, promptPartIds, frameworkItemId, options, callback) {
        const url = assembleUrl(
            llmId,
            promptPartIds,
            frameworkItemId,
            options,
            false
        );
        fetch(url)
        .then(response => response.json())
        .then(data => callback(data))
        .catch(error => console.log(error));
    },

    generateStream(llmId, promptPartIds, frameworkItemId, options, generationProgressHandler, generationSuccessHandler) {
        const url = assembleUrl(
            llmId,
            promptPartIds,
            frameworkItemId,
            options,
            true
        );
        const eventSource = new EventSource(url);
        eventSource.addEventListener("generation_progress", generationProgressHandler);
        eventSource.addEventListener("generation_success", (event) => {
            eventSource.close();
            generationSuccessHandler(event);
        });
    },

    generate(llmId, promptPartIds, frameworkItemId, options, stream, callback, generationProgressHandler, generationSuccessHandler) {
        if (stream) {
            this.generateStream(
                llmId,
                promptPartIds,
                frameworkItemId,
                options,
                generationProgressHandler,
                generationSuccessHandler
            );
        } else {
            this.generateNoStream(
                llmId,
                promptPartIds,
                frameworkItemId,
                options,
                callback
            );
        }
    }
};
