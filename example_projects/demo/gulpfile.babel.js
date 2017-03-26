import 'babel-polyfill';

import ExtractTextPlugin from 'extract-text-webpack-plugin';
import gulp from 'gulp';
import gutil from 'gulp-util';
import path from 'path';
import named from 'vinyl-named';
import webpack from 'webpack';
import webpackStream from 'webpack-stream';


/* Global variables */
const root_dir = './';
const static_dir = root_dir + 'demo/static/';
const templates_dirs = root_dir + 'demo/templates/';

/* Directories */
var build_dir = static_dir + 'build';
var less_dir = static_dir + 'less';
var js_dir = static_dir + 'js';


/*
 * Global webpack config
 * ~~~~~~~~~~~~~~~~~~~~~
 */

var webpackConfig = {
  output: {
    filename: 'js/[name].js',
  },
  resolve: {
    modules: ['node_modules', ],
    extensions: ['.webpack.js', '.web.js', '.js', '.jsx', '.json', 'less', ],
  },
  module: {
    rules: [
      { test: /\.jsx?$/, exclude: /node_modules/, use: 'babel-loader' },
      { test: /\.less$/, use: ExtractTextPlugin.extract({ use: ['css-loader','less-loader'], fallback: 'style-loader', publicPath: '../' }) },
      { test: /\.txt$/, use: 'raw-loader' },
      { test: /\.(png|jpg|jpeg|gif|svg|woff|woff2)([\?]?.*)$/, use: 'url-loader?limit=10000' },
      { test: /\.(eot|ttf|wav|mp3|otf)([\?]?.*)$/, use: 'file-loader' },
    ],
  },
  plugins: [
    new ExtractTextPlugin({ filename: 'css/[name].css', disable: false }),
    new webpack.LoaderOptionsPlugin({
      minimize: true
    }),
    new webpack.optimize.UglifyJsPlugin({
      compress: { warnings: false }
    }),
  ],
};


/*
 * Webpack task
 * ~~~~~~~~~~~~
 */

/* Task to build our JS and CSS applications. */
gulp.task('build-webpack-assets', function () {
  return gulp.src([
        less_dir + '/theme.less',
      ])
    .pipe(named())
    .pipe(webpackStream(webpackConfig, webpack))
    .pipe(gulp.dest(build_dir));
});


/*
 * Global tasks
 * ~~~~~~~~~~~~
 */

gulp.task('build', ['build-webpack-assets', ]);
