import Vue from 'vue'
import router from './router'
import App from './App.vue'
import {BreakpointPlugin} from "vue-breakpoint";
import VueApexCharts from 'vue-apexcharts';

Vue.use(BreakpointPlugin);
Vue.use(VueApexCharts);
Vue.component('apexchart', VueApexCharts);

new Vue({
    el: '#app',
    router,
    template: '<App/>',
    components: {App}
});
