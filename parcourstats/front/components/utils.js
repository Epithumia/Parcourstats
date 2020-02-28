let axios = require('axios');

module.exports = {
    checkPerm: function (p, t) {
        let prefix;
        // noinspection JSUnresolvedVariable
        if (!t.$route.params.prefix) {
            prefix = '';
        } else {
            prefix = '/' + t.$route.params.prefix;
        }
        // noinspection JSUnresolvedVariable
        // noinspection JSUnresolvedFunction
        let promise = axios.post(prefix + '/api/checkperm', {'permission': p});
        promise.then(response => {
            let data = response.data;
            t.permission = data.permission;
        }).catch(error => {
            console.log(error);
        })
    },
    getPrefix: function (params_prefix) {
        let prefix;
        if (!params_prefix) {
            prefix = '';
        } else {
            prefix = '/' + params_prefix;
        }
        return prefix;
    }
};
