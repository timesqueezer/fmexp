import {
    createRouter,
    createWebHistory,
} from 'vue-router'

import ContentLoader from './components/content-loader'

const routes = [
    {
        path: '/:path(.*)*',
        component: ContentLoader,
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
