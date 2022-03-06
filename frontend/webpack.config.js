const resolve = require('path').resolve
const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const url = require('url')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const publicPath = ''

module.exports = (options = {}) => ({
    entry: {
        vendor: './src/vendor',
        index: './src/main.js'
    },
    output: {
        path: resolve(__dirname, 'dist'),
        filename: options.dev ? '[name].js' : '[name].js?[chunkhash]',
        chunkFilename: '[id].js?[chunkhash]',
        publicPath: options.dev ? '/assets/' : publicPath
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                use: ['vue-loader']
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                include: [resolve('src'), resolve('test'), resolve('/node_modules/vue-ionicons/dist/ionicons-mixin.js')]
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader', 'postcss-loader']
            },
            {
                test: /\.(png|jpg|jpeg|gif|eot|ttf|woff|woff2|svg|svgz)(\?.+)?$/,
                type: 'asset/resource',
            },
            {
                test: /\.sass$/,
                use: ['sass-loader', 'style-loader', 'css-loader', 'postcss-loader']
            },
            {
                test: /\.scss$/,
                use: ['style-loader', 'css-loader', 'sass-loader']
            }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: 'src/index.html'
        }),
        new VueLoaderPlugin()
    ],
    resolve: {
        alias: {
            '~': resolve(__dirname, 'src'),
            '@': resolve(__dirname, 'src/assets'),
            'vue$': 'vue/dist/vue.esm.js'
        },
        extensions: ['.js', '.vue', '.json', '.css', '.png', '.jpg']
    },
    devServer: {
        host: '0.0.0.0',
        port: 8010,
        proxy: {
            '/api': {
                target: 'http://192.168.1.118:5000',
                pathRewrite: {'^/api': ''}
            }
        },
        historyApiFallback: {
            index: url.parse(options.dev ? '/assets/' : publicPath).pathname
        }
    },
    mode: 'development'
})
