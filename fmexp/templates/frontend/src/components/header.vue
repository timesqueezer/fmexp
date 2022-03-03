<script>

import Cookies from 'js-cookie'


export default {
  name: 'Header',
  props: {
    currentUser: { type: Object, required: false, default: null},
    disabled: { type: Boolean, required: true },
  },
  data() {
    return {
      layout: FMEXP_LAYOUT,
    }
  },
  mounted() {},
  methods: {
    logout() {
      window.localStorage.clear()
      Cookies.remove('user_uuid')

      location.href = '/'
    },
  },
}
</script>

<template>
  <nav
    class="navbar navbar-expand-md shadow-sm"
    :class="layout === 'layout1' ? 'navbar-light bg-light' : 'navbar-dark border-bottom'"
  >
    <div class="container">
      <h4 class="m-0">
        <router-link
          class=""
          to="/"
          active-class="active"
          :class="layout === 'layout1' ? 'navbar-brand badge badge-lg bg-warning' : 'me-5'"
        >
          <span v-if="layout === 'layout1'" class="">FM Exp 1</span>
          <span v-if="layout === 'layout2'" class="">FM Exp 2</span>
        </router-link>
      </h4>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar" aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse justify-content-md-center pt-3 pt-md-0" id="navbar">
        <ul class="navbar-nav">
          <li class="nav-item">
            <router-link class="nav-link" to="/" active-class="active">About</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/blog" active-class="active">Blog</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/contact" active-class="active">Contact / Imprint</router-link>
          </li>
        </ul>

        <div class="flex-grow-1"></div>

        <div v-if="currentUser" class="d-flex pt-3 pt-md-0">
          <router-link class="nav-link me-3" to="/profile">
            {{ currentUser.email }}
          </router-link>
          <button class="btn btn-outline-secondary" @click="logout">
            Logout
          </button>
        </div>
        <div v-else class="d-flex">

          <router-link
            class="btn btn-outline-secondary me-3"
            to="/login"
            active-class="active"
            :class="disabled ? 'disabled' : ''"
          >
            Login
          </router-link>

          <router-link
            class="btn btn-outline-secondary"
            to="/register"
            active-class="active"
            :class="disabled ? 'disabled' : ''"
          >
            Register
          </router-link>

        </div>
      </div>
    </div>
  </nav>
</template>
