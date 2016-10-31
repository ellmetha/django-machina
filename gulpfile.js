/* Gulp packages */
'use strict';

/* Include Gulp & Tools we'll use */
var gulp = require('gulp'),
  path = require('path'),
  concat = require('gulp-concat'),
  uglify = require('gulp-uglify'),
  rename = require('gulp-rename'),
  less = require('gulp-less'),
  minifyCSS = require('gulp-minify-css');

/* Global variables */
var application_name = 'machina';

/* Directories */
var static_dir = './machina/static/machina';
var build_dir = static_dir + '/build';
var bower_dir = static_dir + '/_libs';
var less_dir = static_dir + '/less';
var js_dir = static_dir + '/js';


/*
 * Django-machina main assets tasks
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 */

/* Task to build the javascript packages. */
gulp.task('build-js-packages', function () {
  gulp.src([
      bower_dir + '/jquery/dist/jquery.js',
      bower_dir + '/bootstrap/dist/js/bootstrap.js',
    ])
    .pipe(concat(application_name + '.packages.js'))
    .pipe(rename({suffix: '.min'}))
    .pipe(uglify())
    .pipe(gulp.dest(build_dir + '/js'));
});

/* Task to build the main javascript application. */
gulp.task('build-js-application', function () {
  gulp.src(js_dir + '/ui.js')
    .pipe(concat(application_name + '.js'))
    .pipe(rename({suffix: '.min'}))
    .pipe(uglify())
    .pipe(gulp.dest(build_dir + '/js'));
});

/* Task to build the application style. */
gulp.task('build-css', function () {
  gulp.src([
      less_dir + '/admin_theme.less',
      less_dir + '/board_theme.less',
      less_dir + '/board_theme.vendor.less',
    ])
    .pipe(less())
      .pipe(rename({prefix: application_name + '.', suffix: '.min'}))
      .pipe(minifyCSS())
    .pipe(gulp.dest(build_dir + '/css'));
});

/* Task to copy the application fonts. */
gulp.task('build-font', function () {
  gulp.src([
    bower_dir + '/bootstrap/dist/fonts/*',
    bower_dir + '/font-awesome/fonts/*',
  ]).pipe(gulp.dest(build_dir + '/fonts'));
});

/* Task to build our application. */
gulp.task('build-machina-application', ['build-js-packages', 'build-js-application', 'build-css', 'build-font']);


/*
 * Django-machina editor tasks
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~
 */

/* Task to copy the simplemde CSS. */
gulp.task('build-simplemde-css', function () {
  gulp.src(bower_dir + '/simplemde/dist/simplemde.min.css').pipe(gulp.dest(build_dir + '/css/vendor'));
});

/* Task to copy the simplemde JS. */
gulp.task('build-simplemde-js', function () {
  gulp.src(bower_dir + '/simplemde/dist/simplemde.min.js').pipe(gulp.dest(build_dir + '/js/vendor'));
});

/* Task to build the Mardkown editor JS application. */
gulp.task('build-markdown-editor-js-application', function () {
  gulp.src(js_dir + '/editor.js')
    .pipe(concat(application_name + '.editor.js'))
    .pipe(rename({suffix: '.min'}))
    .pipe(uglify())
    .pipe(gulp.dest(build_dir + '/js'));
});

/* Task to build the Mardkown editor application. */
gulp.task('build-machina-editor', ['build-simplemde-css', 'build-simplemde-js', 'build-markdown-editor-js-application']);


/*
 * Global tasks
 * ~~~~~~~~~~~~
 */

/* Default task. */
gulp.task('default', ['build-machina-application', 'build-machina-editor', ]);
