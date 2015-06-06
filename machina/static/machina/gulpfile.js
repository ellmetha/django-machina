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

/* DIRS */
var build_dir = 'build';
var bower_dir = '_libs';
var less_dir = 'less';
var js_dir = 'js';


/* Include all needed javascript packages here. */
var packages_includes = [
    bower_dir + '/jquery/dist/jquery.js',
    bower_dir + '/bootstrap/dist/js/bootstrap.js',
];

/* Include all application related files here. */
var application_includes = [
    js_dir + '/**/*.js',
];

/* Include all of the project styling here. */
var style_includes = [
    less_dir + '/admin_theme.less',
    less_dir + '/board_theme.less',
];

/* Include all of the project fonts here. */
var font_includes = [
    bower_dir + '/bootstrap/dist/fonts/*',
    bower_dir + '/font-awesome/fonts/*',
];

/* Task to build our javascript packages. */
gulp.task('build-js-packages', function () {
    gulp.src(packages_includes)
        .pipe(concat(application_name + '.packages.js'))
        .pipe(rename({suffix: '.min'}))
        .pipe(uglify())
        .pipe(gulp.dest(build_dir + '/js'))
});

/* Task to build our javascript application. */
gulp.task('build-js-application', function () {
    gulp.src(application_includes)
        .pipe(concat(application_name + '.js'))
        .pipe(rename({suffix: '.min'}))
        .pipe(uglify())
        .pipe(gulp.dest(build_dir + '/js'))
});

/* Task to build our application style. */
gulp.task('build-css', function () {
	gulp.src(style_includes)
		.pipe(less())
        .pipe(rename({prefix: application_name + '.', suffix: '.min'}))
        .pipe(minifyCSS())
		.pipe(gulp.dest(build_dir + '/css'));
});

/* Task to copy our application fonts. */
gulp.task('build-font', function () {
    gulp.src(font_includes).pipe(gulp.dest(build_dir + '/fonts'));

});

/* Task to build our application. */
gulp.task('build-application', ['build-js-packages', 'build-js-application', 'build-css', 'build-font']);

/* Default task. */
gulp.task('default', ['build-application', ]);
