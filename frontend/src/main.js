import Vue from 'vue'
import VueRouter from 'vue-router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import App from './App.vue'
import LoginPage from './routes/LoginPage.vue'
import Home from './routes/Home.vue'
import NotFound from './routes/NotFound.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: LoginPage },
  { path: '*', component: NotFound },
]

const router = new VueRouter({
  routes,
});

Vue.use(VueRouter)
Vue.use(ElementUI)

const app = new Vue({
  router,
  render: h => h(App)
}).$mount("#app")
