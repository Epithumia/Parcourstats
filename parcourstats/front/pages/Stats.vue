<!--suppress JSUnresolvedVariable -->
<template>
    <div id="statsModules">
        <b-container>
            <b-row class="text-center">
                <b-col>
                    <p v-if="!choix_formation && ready">
                        Chargement en cours...
                    </p>
                    <b-form-select v-model="selected_formation" :options="choix_formation" class="mb-3"
                                   v-if="choix_formation" @change="extracted">
                    </b-form-select>
                </b-col>
            </b-row>
            <b-card no-body>
                <b-tabs card>
                    <b-tab title="Général">
                        <b-row class="text-center">
                            <b-col>
                                <p v-if="!choix_gen">
                                    Chargement en cours...
                                </p>
                                <b-form-select v-model="selected_gen" :options="choix_gen" class="mb-3"
                                               v-if="choix_gen">
                                </b-form-select>
                            </b-col>
                            <b-col>
                            </b-col>
                        </b-row>
                        <b-row class="text-center">
                            <b-col>
                                <p v-if="!ready_gen">
                                    Chargement en cours...
                                </p>
                                <div v-if="ready_gen">
                                    <apexchart ref="chart" width="100%" type="line" :options="options"
                                               :series="filtered_stats_gen"></apexchart>
                                </div>
                            </b-col>
                        </b-row>
                    </b-tab>
                    <b-tab title="Détails">
                        <b-row class="text-center">
                            <b-col>
                                <p v-if="!series_bac">
                                    Chargement en cours...
                                </p>
                                <b-form-select v-model="selected_serie" :options="series_bac" class="mb-3"
                                               v-if="series_bac">
                                </b-form-select>
                            </b-col>
                            <b-col>
                                <p v-if="!types_bac">
                                    Chargement en cours...
                                </p>
                                <b-form-select v-model="selected_type" :options="types_bac" class="mb-3"
                                               v-if="types_bac">
                                </b-form-select>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col>
                                <p v-if="!ready">
                                    Chargement en cours...
                                </p>
                                <div v-if="ready">
                                    <apexchart ref="chart" width="100%" type="line" :options="options"
                                               :series="filtered_stats"></apexchart>
                                </div>
                            </b-col>
                        </b-row>
                    </b-tab>
                </b-tabs>
            </b-card>
        </b-container>
    </div>
</template>

<script>
    import axios from 'axios';
    import Vue from 'vue'
    import {CardPlugin, FormSelectPlugin, LayoutPlugin, TabsPlugin} from 'bootstrap-vue'

    Vue.use(CardPlugin);
    Vue.use(TabsPlugin);
    Vue.use(FormSelectPlugin);
    Vue.use(LayoutPlugin);

    const utils = require('../components/utils.js');


    export default {
        name: "Stats",
        data() {
            return {
                matieres: null,
                prefix: utils.getPrefix(this.$route.params.prefix),
                selected_serie: '',
                selected_type: '',
                choix_gen: ['', 'Total', 'Confirmés'],
                selected_gen: '',
                choix_formation: [],
                selected_formation: null,
                donnees: null,
                options: {
                    chart: {
                        id: 'stats-parcoursup',
                        animations: {
                            enabled: false
                        }
                    },
                    xaxis: {
                        type: 'datetime',
                    },
                    yaxis: {
                        min: 0,
                        tickAmount: 10
                    },
                    legend: {
                        position: 'bottom',
                        show: true
                    },
                    dataLabels: {
                        enabled: false,
                    },
                    markers: {
                        size: 3,
                    },
                    stroke: {
                        curve: 'smooth',
                        width: 2
                    },
                },
                series: [],
                series_bac: [],
                types_bac: [],
                stats_gen: [],
                ready: false,
                ready_gen: false,
            }
        },
        methods: {
            loadData: function () {
                // noinspection JSUnresolvedVariable
                let promise = axios.get(this.prefix + '/api/stats');
                return promise.then(data => {
                    this.donnees = data.data;
                    let formations = this.donnees.liste_f;
                    let choix_f_t = [];
                    this.choix_formation = choix_f_t;
                    for (let f in formations) {
                        choix_f_t.push({'value': formations[f][0], 'text': formations[f][1]});
                    }
                    if (!this.selected_formation) this.selected_formation = choix_f_t[0].value;

                    this.extracted();
                    this.ready = true;
                    this.ready_gen = true;
                }).catch(error => {
                    console.log(error);
                });
            },
            extracted: function () {
                let stats = this.donnees.liste_stats[this.selected_formation];
                let bacs = stats.data;
                let t_series = [];
                let t_series_bac = stats.series;
                t_series_bac.unshift('');
                this.selected_serie = '';
                let t_types_bac = stats.types;
                t_types_bac.unshift('');
                for (let bac in bacs) {
                    let s = [];
                    for (let stamp in bacs[bac]) {
                        let date = new Date(stamp * 1);
                        s.push([date, bacs[bac][stamp]])
                    }
                    t_series.push({name: bac, data: s})
                }
                let genstats = stats.general;
                let t_gen = [];
                for (let c in genstats) {
                    let s = [];
                    for (let stamp in genstats[c]) {
                        let date = new Date(stamp * 1);
                        s.push([date, genstats[c][stamp]])
                    }
                    t_gen.push({name: c, data: s})
                }
                this.series = t_series;
                this.series_bac = t_series_bac;
                this.types_bac = t_types_bac;
                this.stats_gen = t_gen;

            }

        },
        mounted: function () {
            //Initial Load
            this.loadData();
            this.prefix = utils.getPrefix(this.$route.params.prefix);

            //Run every 3600 seconds
            setInterval(function () {
                this.loadData();
            }.bind(this), 3600000);
        },
        computed: {
            filtered_stats: function () {
                let t_series = [];
                let sel_serie = '';
                let sel_type = '';
                if (this.selected_serie.length > 0) sel_serie = this.selected_serie;
                if (this.selected_type.length > 0) sel_type = '- ' + this.selected_type + ' -';
                for (let bac in this.series) {
                    if (this.series[bac].name.includes(sel_serie) && this.series[bac].name.includes(sel_type)) {
                        t_series.push(this.series[bac]);
                    }
                }
                return t_series;
            },
            filtered_stats_gen: function () {
                let sel = '';
                let t = [];
                if (this.selected_gen === 'Total') sel = 'total';
                if (this.selected_gen === 'Confirmés') sel = 'confirmés';
                for (let s in this.stats_gen) {
                    if (this.stats_gen[s].name.includes(sel)) {
                        t.push(this.stats_gen[s]);
                    }
                }
                return t;
            }
        }
    }
</script>
