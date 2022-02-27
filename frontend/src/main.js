import Vue from 'vue'
import VueRouter from 'vue-router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import App from './App.vue'
import LoginPage from './routes/LoginPage'
import Home from './routes/Home.vue'
import NotFound from './routes/NotFound'
import ProfilePage from "./routes/Profile"
import EditProfilePage from "./routes/EditProfile";
import BulletinViewPage from "./routes/BulletinView";
import BulletinEditPage from "./routes/BulletinEdit";
import ProblemsPage from "./routes/Problems";
import ProblemViewPage from "./routes/ProblemView";
import ProblemEditPage from "./routes/ProblemEdit";


const routes = [
    {path: '/', component: Home},
    {path: '/problems', component: ProblemsPage},
    {path: '/problems/edit', component: ProblemEditPage},
    {path: '/problems/view', component: ProblemViewPage},
    {path: '/profile/edit', component: EditProfilePage},
    {path: '/profile', component: ProfilePage},
    {path: '/bulletins/view', component: BulletinViewPage},
    {path: '/bulletins/edit', component: BulletinEditPage},
    {path: '/login', component: LoginPage},
    {path: '*', component: NotFound},
]

const router = new VueRouter({
    routes,
});

Vue.use(VueRouter)
Vue.use(ElementUI)

new Vue({
    router,
    render: h => h(App)
}).$mount("#app")
