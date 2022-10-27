import Vue from 'vue'
import VueRouter from 'vue-router'

import clipboard from 'clipboard';
//注册到vue原型上
Vue.prototype.clipboard = clipboard;

import './oj-theme/theme.css';

import ElementUI from 'element-ui';
import App from './App.vue';
import LoginPage from './routes/LoginPage';
import RegisterPage from './routes/RegisterPage';
import Home from './routes/Home.vue';
import NotFound from './routes/NotFound';
import ProfilePage from "./routes/Profile";
import EditProfilePage from "./routes/EditProfile";
import BulletinViewPage from "./routes/BulletinView";
import BulletinEditPage from "./routes/BulletinEdit";
import ProblemsPage from "./routes/Problems";
import ProblemViewPage from "./routes/ProblemView";
import ProblemEditPage from "./routes/ProblemEdit";
import JudgeRecordViewPage from "./routes/JudgeRecordView";
import JudgeMachines from "./routes/JudgeMachines";
import RecordsPage from "./routes/Records";
import ProblemListsPage from "./routes/ProblemLists";
import ProblemListEditPage from "./routes/ProblemListEdit";
import ProblemListViewPage from "./routes/ProblemListView";
import ArticlesPage from "./routes/Articles";
import ArticleViewPage from "./routes/ArticleView";
import ArticleEditPage from "./routes/ArticleEdit";
import ContestsPage from "./routes/Contests";
import ContestViewPage from "./routes/ContestView";
import ContestEditPage from "./routes/ContestEdit";
import ContestProblemViewPage from "./routes/ContestProblemView";
import RatingsPage from "./routes/Ratings";
import OnlineIDE from "./routes/OnlineIDE";

const routes = [
    {path: '/', component: Home},
    {path: '/articles', component: ArticlesPage},
    {path: '/articles/view', component: ArticleViewPage},
    {path: '/articles/edit', component: ArticleEditPage},
    {path: '/lists', component: ProblemListsPage},
    {path: '/lists/edit', component: ProblemListEditPage},
    {path: '/lists/view', component: ProblemListViewPage},
    {path: '/problems', component: ProblemsPage},
    {path: '/problems/edit', component: ProblemEditPage},
    {path: '/problems/view', component: ProblemViewPage},
    {path: '/profile/edit', component: EditProfilePage},
    {path: '/profile', component: ProfilePage},
    {path: '/bulletins/view', component: BulletinViewPage},
    {path: '/bulletins/edit', component: BulletinEditPage},
    {path: '/records', component: RecordsPage},
    {path: '/records/view', component: JudgeRecordViewPage},
    {path: '/ratings', component: RatingsPage},
    {path: '/contests', component: ContestsPage},
    {path: '/contests/view', component: ContestViewPage},
    {path: '/contests/edit', component: ContestEditPage},
    {path: '/contests/solve', component: ContestProblemViewPage},
    {path: '/machines', component: JudgeMachines},
    {path: '/login', component: LoginPage},
    {path: '/register', component: RegisterPage},
    {path: '/ide', component: OnlineIDE},
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
