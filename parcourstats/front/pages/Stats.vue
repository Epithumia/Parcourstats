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
          <b-tab title="Répartitions">
            <b-row class="text-center">
              <b-col>
                <p v-if="!groupes">
                  Chargement en cours...
                </p>
                <b-form-select v-model="selected_groupe_rep" :options="groupes" class="mb-3"
                               v-if="groupes">
                </b-form-select>
              </b-col>
              <b-col>
              </b-col>
            </b-row>
            <b-row>
              <b-col>
                <p v-if="!ready">
                  Chargement en cours...
                </p>
                <div v-if="ready">
                  <apexchart ref="chart" width="100%" :options="options_repartition"
                             :series="filtered_stats_rep"></apexchart>
                </div>
              </b-col>
            </b-row>
          </b-tab>
          <b-tab title="Admissions" v-if="groupes.length>0&&stats_adm.length>0">
            <b-row class="text-center">
              <b-col>
                <p v-if="!groupes">
                  Chargement en cours...
                </p>
                <b-form-select v-model="selected_groupe" :options="groupes" class="mb-3"
                               v-if="groupes">
                </b-form-select>
              </b-col>
              <b-col>
              </b-col>
            </b-row>
            <b-row>
              <b-col>
                <p v-if="!ready">
                  Chargement en cours...
                </p>
                <div v-if="ready">
                  <apexchart ref="chart" width="100%" type="line" :options="options"
                             :series="filtered_stats_adm"></apexchart>
                </div>
              </b-col>
            </b-row>
          </b-tab>
        </b-tabs>
      </b-card>
    </b-container>
  </div>
</template>

<!--suppress JSUnusedGlobalSymbols -->
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
      selected_groupe: '',
      selected_groupe_rep: '',
      choix_gen: ['', 'Total', 'Confirmés'],
      selected_gen: '',
      choix_formation: [],
      selected_formation: null,
      donnees: null,
      admissions: null,
      repartitions: null,
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
      options_repartition: {
        chart: {
          id: 'stats-repartition',
          type: 'bar',
          stacked: true,
          stackType: '100%'
        },
        xaxis: {
          type: 'category',
          categories: [
            "Répartition Néo/Anté",
            "Série du bac",
            "Spécialités"
          ],
          tickPlacement: 'between'
        },
        legend: {
          position: 'right',
          show: false,
          offsetX: -100,
          offsetY: 50
        },
        dataLabels: {
          enabled: true,
          formatter: function (val) {
            return val ? val.toFixed(2) + '%' : ''
          }
        },
        title: {
          text: 'Stats - Réparition des bacs',
          'align': 'center'
        }
      },
      rep_categories: [
        "Répartition Néo/Anté",
        "Série du bac",
        "Spécialités"
      ],
      series: [],
      series_bac: [],
      stats_repartition: [],
      types_bac: [],
      groupes: [],
      stats_gen: [],
      stats_adm: [],
      ready: false,
      ready_gen: false,
    }
  },
  methods: {
    loadData: function () {
      // noinspection JSUnresolvedVariable
      let promise = axios.all([
        axios.get(this.prefix + '/api/stats'),
        axios.get(this.prefix + '/api/admissions'),
        axios.get(this.prefix + '/api/repartition')
      ]);
      promise.then(axios.spread((stats, admissions, repartition) => {
        this.donnees = stats.data;
        this.admissions = admissions.data;
        this.repartitions = repartition.data;
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
      })).catch(error => {
        console.log(error);
      });
    },
    extracted: function () {
      let stats = this.donnees.liste_stats[this.selected_formation];
      let arr_groupes_t = this.admissions.liste_f[this.selected_formation][1];
      let admissions = this.admissions.liste_stats[this.selected_formation];
      let repartitions = this.repartitions.liste_stats[this.selected_formation];
      let t_repartitions = [];
      for (let gr of Object.keys(repartitions)) {
        let entry = Object.entries(repartitions[gr])[0];
        let t_gr = entry[0];
        let t_data = entry[1];
        let t_stats_rep = t_data.stats;
        let t_labels = t_data.labels;
        let t_serie_rep = []
        for (const label of t_labels) {
          let t_row = [];
          for (const cat of this.rep_categories) {
            t_row.push(t_stats_rep[label][cat]);
          }
          t_serie_rep.push({name: label, data: t_row});
        }
        t_repartitions.push({name: t_gr, data: t_serie_rep});
      }
      let groupes_t = [];
      let t_adm_etats = [];
      let t_adm_decisions = [];
      for (let g in arr_groupes_t) {
        groupes_t.push({value: arr_groupes_t[g][0], text: arr_groupes_t[g][1]});
      }
      if (groupes_t.length > 0) groupes_t.unshift({value: -1, text: 'Total'});
      for (let gr in admissions) {
        let entry = Object.entries(admissions[gr])[0];
        let t_gr = entry[0];
        let t_data = entry[1];
        let t_decisions = [];
        for (let k in t_data.decisions) {
          let s = [];
          for (let stamp in t_data.decisions[k]) {
            let date = new Date(stamp * 1);
            s.push([date, t_data.decisions[k][stamp]]);
          }
          t_decisions.push({name: 'Décision : ' + k, data: s});
        }
        t_adm_decisions.push({name: t_gr, data: t_decisions});
        let t_etats = [];
        for (let k in t_data.etats) {
          let s = [];
          for (let stamp in t_data.etats[k]) {
            let date = new Date(stamp * 1);
            s.push([date, t_data.etats[k][stamp]]);
          }
          t_etats.push({name: 'Etat : ' + k, data: s});
        }
        t_adm_etats.push({name: t_gr, data: t_etats});
      }
      this.stats_adm = {etat: t_adm_etats, decisions: t_adm_decisions};
      this.groupes = groupes_t;
      if (groupes_t.length > 0) {
        this.selected_groupe = groupes_t[0].value;
        this.selected_groupe_rep = groupes_t[0].value;
      }
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
      this.stats_repartition = t_repartitions;
      if (t_series[0].data.length * t_series.length > 1000) {
        this.options.markers.size = 0;
      }
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
      if (this.selected_serie.length > 0) sel_serie = this.selected_serie + ' -';
      if (this.selected_type.length > 0) sel_type = '- ' + this.selected_type + ' -';
      for (let bac in this.series) {
        if (this.series[bac].name.startsWith(sel_serie) && this.series[bac].name.includes(sel_type)) {
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
    },
    filtered_stats_adm: function () {
      let sel = '';
      let t = [];
      sel = this.selected_groupe;
      if (this.stats_adm.etat.length > 0) {
        for (let row of this.stats_adm.etat) {
          if (row.name === sel.toString()) {
            for (let serie of row.data) t.push(serie);
          }
        }
      }
      if (this.stats_adm.decisions.length > 0) {
        for (let row of this.stats_adm.decisions) {
          if (row.name === sel.toString()) {
            for (let serie of row.data) t.push(serie);
          }
        }
      }
      return t;
    },
    filtered_stats_rep: function () {
      let sel = '';
      let t = [];
      sel = this.selected_groupe_rep;
      if (this.stats_repartition.length > 0) {
        for (let row of this.stats_repartition) {
          if (row.name === sel.toString()) {
            return row.data;
          }
        }
      }
      return t;
    }
  }
}
</script>
