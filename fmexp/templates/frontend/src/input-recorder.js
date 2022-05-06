import axios from 'axios'
import Cookies from 'js-cookie'
import {
  throttle
} from 'lodash'


export default class InputRecorder {
  constructor() {
    this.eventList = []
    this.dataSenderTimeout = null
    this.userUUID = null

  }

  async init() {
    await this.setUserUUID()

    this.setupListeners()
    this.setupDataSender()
  }

  async setUserUUID() {
    const alreadySetUserUUID = Cookies.get('user_uuid')
    if (alreadySetUserUUID) {
      this.userUUID = alreadySetUserUUID

    } else {
      console.warn('UUID Cookie not set!')
      /* const response = await axios.post('/user-uuid')
      this.userUUID = response.data.user_uuid
      Cookies.set('user_uuid', this.userUUID) */

    }
  }

  setupListeners() {
    this.addEventListener('pointermove', this.onPointerMove, true)
    this.addEventListener('pointerdown', this.onPointerDown)
    this.addEventListener('pointerup', this.onPointerUp)
  }

  addEventListener(eventType, fn, throttled) {
    const maxEventsPerSecond = 30
    const timeout = 1000 / maxEventsPerSecond

    document.addEventListener(
      eventType,
      throttled ? throttle(fn.bind(this), timeout) : fn.bind(this),
      { passive: true },
    )
  }

  setupDataSender() {
    this.dataSenderTimeout = window.setTimeout(this.sendData.bind(this), 2000)
  }

  async sendData() {
    if (this.eventList.length) {
      const data = this.eventList
      this.eventList = []

      const payload = {
        meta: {
          user_uuid: this.userUUID,
        },
        data,
      }

      await axios.post('/data-capture', payload)

    }

    this.setupDataSender()
  }

  pushEvent(data) {
    this.eventList.push({
      dt: (new Date()).toISOString(),
      data,
    })
  }

  onPointerMove(e) {
    this.pushEvent({
      type: 'move',
      position: { x: e.clientX, y: e.clientY },
      position_absolute: { x: e.pageX, y: e.pageY },
      screen: { width: e.view.innerWidth, height: e.view.innerHeight },
      pointer_type: e.pointerType,
    })
  }

  onPointerDown(e) {
    const div = document.createElement('div')
    div.style.position = 'absolute'
    div.style.top = e.clientY + 'px'
    div.style.left = e.clientX + 'px'
    div.style.width = '20px'
    div.style.height = '20px'
    div.style.background = 'red'
    document.body.appendChild(div)

    console.log('div', div)

    this.pushEvent({
      type: 'pointerdown',
      position: { x: e.clientX, y: e.clientY },
      position_absolute: { x: e.pageX, y: e.pageY },
      screen: { width: e.view.innerWidth, height: e.view.innerHeight },
      pointer_type: e.pointerType,
      buttons: e.buttons,
    })
  }

  onPointerUp(e) {
    this.pushEvent({
      type: 'pointerdown',
      position: { x: e.clientX, y: e.clientY },
      position_absolute: { x: e.pageX, y: e.pageY },
      screen: { width: e.view.innerWidth, height: e.view.innerHeight },
      pointer_type: e.pointerType,
      buttons: e.buttons,
    })
  }
}
