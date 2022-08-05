const pt = require('puppeteer');
const gc = require('ghost-cursor');

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const randomDelay = async () => {
    const min = 0
    const max = 200
    await delay(
        Math.random() * (max - min) + min
    )
};
const range = n => [...Array(n).keys()];


(async () => {
    const browser = await pt.launch({
        headless: false,
    })

    const args = process.argv.slice(2)
    const targetHost = args[0]
    const width = parseInt(args[1])
    const height = parseInt(args[2])
    const methods = args.slice(3)

    console.log('args', args)
    console.log('targetHost', targetHost)
    console.log('width', width)
    console.log('height', height)
    console.log('methods', methods)

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

            for i in range(num_pages):
                all_link_els = self.find_elements_by_xpath('//main//a')
                selected_link = random.choice(all_link_els)

                self.move_click(selected_link)

                self.back()

        } else if (method === 'visit_random_pages') {
            
        } else if (method === 'register') {
            
        } else if (method === 'register_and_fill_in_profile') {
            
        }
    }

    await browser.close()

})()
