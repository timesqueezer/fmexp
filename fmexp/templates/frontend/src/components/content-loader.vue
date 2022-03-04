<script>
import axios from 'axios'

import VRuntimeTemplate from 'vue3-runtime-template'


export default {
  name: 'ContentLoader',
  components: {
    VRuntimeTemplate,
  },
  props: {
    user: { type: Object, required: false, default: null },
  },
  data() {
    return {
      layout: FMEXP_LAYOUT,

      content: '',
      errorMessage: null,
      currentUser: null,

      profileSuccessMessage: null,
      passwordSuccessMessage: null,
    }
  },
  created() {
    this.currentUser = this.user

    this.$watch(
      () => this.$route.params,
      () => {
        this.loadSite()
      },
      { immediate: true },
    )
  },
  mounted() {
    this.currentUser = this.user
  },
  methods: {
    async loadSite() {
      this.errorMessage = null

      const path = this.$route.path === '/' ? '/home' : this.$route.path

      const restrictedLoggedinPaths = [
        '/login',
        '/register',
      ]

      const restrictedLoggedOutPaths = [
        '/profile',
      ]

      if (
        (this.currentUser && restrictedLoggedinPaths.indexOf(path) !== -1) ||
        (!this.currentUser && restrictedLoggedOutPaths.indexOf(path) !== -1)
      ) {
        this.$router.replace('/')

      } else {
        const response = await axios.get('/content' + path)
        this.content = response.data

      }

    },
    showSuccessMessage(attr, message, timeout) {
      timeout = timeout || 3000
      this[attr] = message
      setTimeout(() => {
        this[attr] = null
      }, timeout)
    },
    async loginAs(email, password) {
      const response = await axios.post(
        '/auth',
        { email, password },
      )
      .catch((error) => {
        if (error.response?.data?.description) {
          this.errorMessage = error.response.data.description

        }

      })

      if (response.status === 200 && response?.data?.token) {
        window.localStorage.setItem('fmexp_jwt_token', response.data.token)
        axios.defaults.headers.common.Authorization = 'JWT ' + response.data.token

      }

    },
    async login(e) {
      this.errorMessage = null

      const formData = new FormData(e.target)
      const data = Object.fromEntries(formData.entries())

      await this.loginAs(data.email.toLowerCase(), data.password)
      const currentUserResponse = await axios.get('/user')

      if (currentUserResponse) {
        this.$emit('set-user', currentUserResponse.data)
        this.currentUser = currentUserResponse.data

      }

      this.$router.replace('/profile')

    },
    setCustomValidities(errors) {
      Object.keys(errors).forEach((fieldName) => {
        const el = document.querySelector('#' + fieldName)
        if (el) {
          el.setCustomValidity(errors[fieldName][0])
          el.reportValidity()
        }

      })
    },
    async register(e) {
      this.errorMessage = null

      const formData = new FormData(e.target)
      const email = formData.get('email')
      formData.set('email', email.toLowerCase())
      const data = Object.fromEntries(formData.entries())

      const response = await fetch(
        '/register',
        {
          method: 'POST',
          body: formData,
        }
      )
      .catch((error) => {
        console.log(error)

      })

      // try {
        const responseData = await response.json()

        if (response.status == 200) {
          await this.loginAs(data.email, data.password)
          this.$emit('set-user', responseData)
          this.currentUser = responseData
          this.$router.replace('/profile')

        } else {
          if (responseData.errors) {
            this.setCustomValidities(responseData.errors)

          }

        }

      /*} catch {
        this.errorMessage = 'An error occurred. Please try again.'

      }*/
    },
    async editProfile(editMode, e) {
      this.errorMessage = null

      const formData = new FormData(e.target)
      const data = Object.fromEntries(formData.entries())

      const url = editMode === 'profile' ? '/user' : '/password'

      const response = await fetch(
        url,
        {
          method: 'POST',
          body: formData,
          headers: {
            ...axios.defaults.headers.common,
          },
        }
      )
      .catch((error) => {
        console.log(error)

      })


      // try {
        if (response.status === 200 || response.status === 204) {
          if (editMode === 'profile') {
            const responseData = await response.json()
            this.loadSite()
            this.showSuccessMessage('profileSuccessMessage', 'Profile saved')
            this.$emit('set-user', responseData)

          } else {
            this.showSuccessMessage('passwordSuccessMessage', 'Password saved')

          }

        } else {
          const responseData = await response.json()
          if (responseData.errors) {
            this.setCustomValidities(responseData.errors)

          }

        }
    },
    resetValidity(e) {
      e.target.setCustomValidity('')
    },
  }
}
</script>

<template>
  <v-runtime-template :template="this.content"></v-runtime-template>
</template>
