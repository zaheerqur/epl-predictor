import { createRouter, createWebHistory } from 'vue-router'
import AboutView    from '../views/AboutView.vue'
import PredictView  from '../views/PredictView.vue'
import BacktestView from '../views/BacktestView.vue'
import TableView    from '../views/TableView.vue'
import TeamsView    from '../views/TeamsView.vue'
import PipelineView from '../views/PipelineView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          redirect: '/about' },
    { path: '/about',     component: AboutView },
    { path: '/predict',   component: PredictView },
    { path: '/backtest',  component: BacktestView },
    { path: '/table',     component: TableView },
    { path: '/teams',     component: TeamsView },
    { path: '/pipeline',  component: PipelineView },
  ],
})
