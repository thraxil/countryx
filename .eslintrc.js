module.exports = {
    "env": {
        "browser": true,
        "jquery": true
    },
    "extends": "eslint:recommended",
    "globals": {
        "addElementClass": true,
        "addLoadEvent": true,
        "connect": true,
        "doXHR": true,
        "evalJSON": true,
        "forEach": true,
        "getCookie": true,        
        "getElementsByTagAndClassName": true,
        "getFirstElementByTagAndClassName": true,
        "getStyle": true,
        "hasElementClass": true,
        "hideElement": true,
        "log": true,
        "MochiKit": true,
        "queryString": true,
        "removeElementClass": true,
        "replaceChildNodes": true,
        "serializeJSON": true,
        "setNodeAttribute": true,
        "setStyle": true,
        "setCookie": true,
        "showElement": true,
        "toggle": true,
    },
    "rules": {
        "indent": [
            "error",
            4
        ],
        "linebreak-style": [
            "error",
            "unix"
        ],
        "no-unused-vars": [
            "error",
            {"vars": "all", "args": "none"}
        ],
        "quotes": [
            "error",
            "single"
        ],
        "semi": [
            "error",
            "always"
        ]
    }
};
