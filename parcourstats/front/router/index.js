import Vue from 'vue'
import Router from 'vue-router'

// Chargement dynamique
const Stats = resolve => require(['../pages/Stats.vue'], resolve);


// noinspection JSUnresolvedFunction
Vue.use(Router);

export default new Router({
    mode: 'history',
    routes: [

        {
            path: '/:prefix?/stats',
            name: 'Statistiques',
            component: Stats
        },

    ]
})
