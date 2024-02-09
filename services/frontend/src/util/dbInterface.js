import { host } from "./util";

const dbInterfacePort = 5003;

function makeAndHandleRequest(endpoint, method, body) {
    return fetch(`http://${host()}:${dbInterfacePort}${endpoint}`, {
        method: method,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    })
    .then(response => response.json())
    .catch(error => console.log(error));
}

export const db = {
    getById(modelName, id) {
        return makeAndHandleRequest(
            `/${modelName}/${id}`,
            "GET",
            null
        );
    },

    getAll(modelName) {
        return makeAndHandleRequest(
            `/${modelName}`,
            "GET",
            null
        );
    },

    getByName(modelName, name) {
        return makeAndHandleRequest(
            `/${modelName}/by-name/${name}`,
            "GET",
            null
        );
    },

    create(modelName, data) {
        return makeAndHandleRequest(
            `/${modelName}`,
            "POST",
            data
        );
    }
}
