const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const TerserPlugin = require('terser-webpack-plugin');
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const {VueLoaderPlugin} = require('vue-loader');
require("babel-polyfill");

// noinspection WebpackConfigHighlighting
module.exports = {
    entry: ["babel-polyfill", './parcourstats/front/main.js'],
    output: {
        path: path.resolve(__dirname, './parcourstats/static/front/'),
        publicPath: '/static/front/',
        filename: 'build.js',
        chunkFilename: "[name].js"
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
                options: {
                    loaders: {}
                    // other vue-loader options go here
                }
            },
            process.env.NODE_ENV === 'production' ? { test: /\.js$/, exclude: /node_modules/, use: 'babel-loader' } : {},
            {
                test: /\.js$/,
                //loader: 'babel-loader',
                exclude: /node_modules/,
                use: [
                    'ify-loader' ,
                    'transform-loader?plotly.js/tasks/compress_attributes.js',
                ]
            },
            {
                test: /\.css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            // you can specify a publicPath here
                            // by default it use publicPath in webpackOptions.output
                            publicPath: '../'
                        }
                    },
                    "css-loader"
                ]
            },
            {
                test: /\.(png|jpg|gif|svg)$/,
                loader: 'file-loader',
                options: {
                    name: '[name].[ext]?[hash]'
                }
            }
        ]
    },
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js'
        }
    },
    devServer: {
        historyApiFallback: true,
        noInfo: true
    },
    performance: {
        hints: false
    },
    optimization: {
        splitChunks: {
            cacheGroups: {
                commons: {
                    test: /[\\/]node_modules[\\/]/,
                    name: "vendor",
                    chunks: "initial",
                }
            }
        },
        minimizer: [
            new TerserPlugin({
                cache: true,
                parallel: true,
                sourceMap: true
            }),
            new OptimizeCSSAssetsPlugin({})
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: '[name].css',
            chunkFilename: '[id].css'}
        ),
        new VueLoaderPlugin(),
        new BundleAnalyzerPlugin({
            openAnalyzer: process.env.NODE_ENV === 'stats',
            analyzerMode: process.env.NODE_ENV === 'stats' ? 'server' : 'disabled'
        })
    ],
    devtool: '#eval-source-map'
};

if (process.env.NODE_ENV === 'production') {
    module.exports.devtool = '#source-map';
    module.exports.output.publicPath = '/parcourstats/static/front/';
    // http://vue-loader.vuejs.org/en/workflow/production.html
    // noinspection JSUnresolvedFunction
    module.exports.plugins = (module.exports.plugins || []).concat([
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"production"'
            }
        }),
    ])
}
