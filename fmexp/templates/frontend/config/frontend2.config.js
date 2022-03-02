const webpack = require('webpack')

const baseConfig = require('./webpack.config.js')

baseConfig.plugins.push(
    new webpack.DefinePlugin({
        FMEXP_LAYOUT: 'layout2',
    })
)

module.exports = baseConfig
