<script>
  import axios from 'axios'
  import Cookies from 'js-cookie'
  import { path } from 'ghost-cursor'

  import Header from './components/header'

  import InputRecorder from './input-recorder'


  export default {
    components: {
      Header,
    },
    data() {
      return {
        layout: FMEXP_LAYOUT,

        loading: true,
        showConsentAlert: false,

        inputRecorder: null,
        currentUser: null,

        isBot: null,
      }
    },
    async created() {
      // await this.init()
      if (!window.localStorage.getItem('fmexp_consent')) {
        this.showConsentAlert = true

      } else {
        await this.init()

      }

      this.loading = false

    },
    methods: {
      async init() {
        this.inputRecorder = new InputRecorder()
        await this.inputRecorder.init()

        if (window.localStorage.getItem('fmexp_jwt_token')) {
          axios.defaults.headers.common.Authorization = 'JWT ' + window.localStorage.getItem('fmexp_jwt_token')
          const currentUserResponse = await axios.get('/user')
          .catch((error) => {
            // reset on error, which "should" never happen
            window.localStorage.removeItem('fmexp_jwt_token')
            delete axios.defaults.headers.common.Authorization
            Cookies.remove('user_uuid')

            location.href = '/'

          })

          if (currentUserResponse) {
            this.currentUser = currentUserResponse.data

          }

        }
      },
      setUser(user) {
        this.currentUser = user
        Cookies.set('user_uuid', user.uuid)
      },
      async consent() {
        window.localStorage.setItem('fmexp_consent', true)
        await this.init()
        this.showConsentAlert = false

        /* const div = document.createElement('div')
        div.style.position = 'absolute'
        div.style.top = '0px'
        div.style.left = '0px'
        div.style.width = '40px'
        div.style.height = '40px'
        div.style.background = 'green'
        document.body.appendChild(div) */
      },
      updateIsBot(isBot) {
        this.isBot = isBot
      },
      testMouse() {
        const route = path(
          { x: 100, y: 100 },
          { x: 1000, y: 500 },
        )
        console.log('route', route)
      },
    }
  }
</script>

<template>
  <Header :current-user="currentUser" :disabled="showConsentAlert"></Header>

  <main class="container flex-shrink-0 pt-3">
    <div v-if="loading">
      Loading
    </div>
    <div v-else>
      <button @click="testMouse">Test Mouse</button>
      <div v-if="showConsentAlert" class="row">

        <div class="col-xs-12 col-sm-8 mx-auto">
          <div class="bg-white shadow-sm p-4 text-center">
            <h1 class="mb-4 fw-bold">Welcome and Thank You for Participating</h1>
            <p class="lead mb-4">My Name is Matz and I am conducting an experiment for my bachelor's thesis. Please browse this website as if it was real and feel free to register and update your profile information. To learn more visit the about page.</p>
            <button id="consentButton" class="btn btn-primary btn-lg" @click="consent">Let's go</button>
          </div>
        </div>

      </div>
      <div v-else class="mb-5">

        <router-view
          :user="currentUser"
          @set-user="setUser"
          @update-is-bot="updateIsBot"
        ></router-view>

      </div>
    </div>
  </main>

  <footer
    class="mt-auto py-3 shadow-sm border-top"
    :class="layout === 'layout1' ? 'bg-light' : 'text-center'"
  >
    <div class="container">
      <span>&copy; 2022 Matz Radloff</span>
      <router-link
        v-if="currentUser && currentUser.email === 'matzradloff@gmail.com'"
        to="/admin"
        class="btn btn-outline-secondary ms-4"
      >Admin</router-link>
      <!--<span class="ms-4">
        Is Bot: <span id="is-bot">{{ isBot }}</span>
      </span>-->
    </div>
  </footer>
</template>
