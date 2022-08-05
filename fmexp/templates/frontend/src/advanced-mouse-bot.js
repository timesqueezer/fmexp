const pt = require('puppeteer');
const gc = require('ghost-cursor');
const faker = require('@faker-js/faker').faker;


const MAX_RANDOM_DELAY = 400

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const randInt = (min, max) => {
    return Math.random() * (max - min) + min
}
const randomDelay = async (max) => {
    const min = 0
    max = max || MAX_RANDOM_DELAY
    await delay(randInt(min, max))
};
const range = n => [...Array(n).keys()];
const randomChoice = (choices) => {
  var index = Math.floor(Math.random() * choices.length)
  return choices[index]
};


(async () => {
    const browser = await pt.launch({
        headless: true,
    })

    const args = process.argv.slice(2)
    const targetHost = args[0]
    const width = parseInt(args[1])
    const height = parseInt(args[2])
    const methods = args.slice(3)

    /* console.log('args', args)
    console.log('targetHost', targetHost)
    console.log('width', width)
    console.log('height', height)
    console.log('methods', methods) */

    const page = await browser.newPage()//.then(async (page) => {

    const cursor = gc.createCursor(page)

    await page.setViewport({
        width,
        height,
    })

    const httpResponse = await page.goto(targetHost + '/?fmexp_bot=true&bot_mode=mouse&random_delays=true&advanced=true')
    // console.log('headers:', httpResponse.headers())
    await page.setCookie({
        'name': 'fmexp_bot',
        'value': '1',
    })
    await randomDelay()

    const moveClick = async (selector) => {
        await randomDelay()
        if (typeof selector === 'string') {
            await page.waitForSelector(selector)
        }
        await cursor.move(selector)
        await cursor.click()
    }

    // click consent
    const consentSelector = '#consentButton'
    await moveClick(consentSelector)
    await randomDelay(200)

    for (const method of methods) {
        if (method === 'visit_pages') {
            const topLevelPages = [
                '/',
                '/blog',
                '/contact',
                '/login',
                '/register',
            ]

            for (tlp of topLevelPages) {
                await delay(100)
                const selector = 'a[href="' + tlp + '"]'
                await moveClick(selector)
            }

        } else if (method === 'visit_blog_pages') {
            await moveClick('a[href="/blog"]')
            await delay(200)

            const numPages = 10


            for (const i of range(numPages)) {
                await delay(200)
                const allLinkEls = await page.$$('main a')
                const selectedLink = randomChoice(allLinkEls)

                await moveClick(selectedLink)
                await page.goBack()
            }

        } else if (method === 'visit_random_pages') {
            const numPages = 100

            for (const i of range(numPages)) {
                // await delay(1000)
                const allLinkEls = await page.$$('a')
                const selectedLink = randomChoice(allLinkEls)
                href = await page.evaluateHandle(el => el.getAttribute('href'), selectedLink)
                if (href && !!href.indexOf && href.indexOf('matzradloff.info') === -1) {
                    await moveClick(selectedLink)
                }
            }

        } else if (method === 'register') {
            const linkEl = 'a[href="/register"]'
            await moveClick(linkEl)
            await delay(200)

            const emailInputEl = await page.$('#email')
            let fakeEmail = faker.internet.email()

            fakeEmailSplit = fakeEmail.split('@')
            fakeEmail = [
                fakeEmailSplit[0],
                randInt(1, 1000000).toString(),
                '@',
                fakeEmailSplit[1],
            ].join('')

            await moveClick(emailInputEl)
            await page.keyboard.type(fakeEmail)

            const password = faker.internet.password(12)

            const emailInputEl1 = await page.$('#password')
            await moveClick(emailInputEl1)
            await page.keyboard.type(password)

            const emailInputEl2 = await page.$('#password2')
            await moveClick(emailInputEl2)
            await page.keyboard.type(password)

            const notRobotEl = await page.$('#not_robot')
            await moveClick(notRobotEl)

            const submitEl = 'button[type=submit]'
            await moveClick(submitEl)

            const logoutEl = '#logout'
            await moveClick(logoutEl)


        } else if (method === 'register_and_fill_in_profile') {

        }
    }

    await browser.close()

})()
