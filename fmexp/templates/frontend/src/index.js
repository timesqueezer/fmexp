import('./scss/' + FMEXP_LAYOUT + '.scss')

import { Collapse } from 'bootstrap'

import * as Vue from 'vue'

import main from './main'
import router from './router'


const app = Vue.createApp(main)
app.use(router)

app.mount('#app')

app.config.errorHandler = (err) => {
  console.error(err)
}
