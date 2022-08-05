const pt = require('puppeteer');
const gc = require('ghost-cursor');
const faker = require('@faker-js/faker').faker;

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const randomDelay = async () => {
    const min = 0
    const max = 200
    await delay(
        Math.random() * (max - min) + min
    )
};
const range = n => [...Array(n).keys()];
const randomChoice = (choices) => {
  var index = Math.floor(Math.random() * choices.length)
  return choices[index]
};


(async () => {
    const browser = await pt.launch({
        headless: false,
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

    await page.goto(targetHost + '/?fmexp_bot=true&bot_mode=mouse&random_delays=true&advanced=true')
    await page.setCookie({
        'name': 'fmexp_bot',
        'value': '1',
    })
    await randomDelay()

    const moveClick = async (selector) => {
        await randomDelay()
        await page.waitForSelector(selector)
        await cursor.move(selector)
        await cursor.click()
    }

    // click consent
    const consentSelector = '#consentButton'
    await moveClick(consentSelector)

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
                const selector = 'a[href="' + tlp + '"]'
                await moveClick(selector)
            }

        } else if (method === 'visit_blog_pages') {
            await moveClick('a[href="/blog"]')

            const numPages = 10


            for (const i of range(numPages)) {
                const allLinkEls = await page.$$('main a')
                const selectedLink = randomChoice(allLinkEls)
                console.log('selectedLink', selectedLink)

                await moveClick(selectedLink)
                await page.goBack()
            }

        } else if (method === 'visit_random_pages') {
            const numPages = 100

            for (const i of range(numPages)) {
                const allLinkEls = await page.$$('a')
                const selectedLink = randomChoice(allLinkEls)
                console.log('selectedLink', selectedLink)
                href = await page.evaluate(el => el.getAttribute('href'), selectedLink)
                if (href.indexOf('matzradloff.info') === -1) {
                    await moveClick(selectedLink)
                }
            }

        } else if (method === 'register') {
            /* const linkEl = 'a[href="/register"]'
            await moveClick(linkEl)

            const email_input_el = self.find_element_by_id('email')
            const emailInputEl = await page.$('#email')
            fake_email = self.fake.email()

            fake_email_split = fake_email.split('@')
            fake_email = ''.join([
                fake_email_split[0],
                str(random.randint(1, 1000000)),
                '@',
                fake_email_split[1],
            ])

            email_input_el.send_keys(fake_email)

            password = '{}_{}'.format(
                self.fake.word(),
                self.fake.word(),
            )

            password1_input_el = self.find_element_by_id('password')
            password1_input_el.send_keys(password)

            password2_input_el = self.find_element_by_id('password2')
            password2_input_el.send_keys(password)

            not_robot_el = self.find_element_by_id('not_robot')
            self.move_click(not_robot_el)

            submit_el = self.find_element_by_xpath('//button[@type="submit"]')
            self.move_click(submit_el) */

        } else if (method === 'register_and_fill_in_profile') {

        }
    }

    await browser.close()

})()
