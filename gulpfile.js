'use strict';

var gulp        = require('gulp');
var plugins     = require('gulp-load-plugins')();
var rimraf      = require('rimraf');
var runSequence = require('run-sequence');
var del         = require('del');
var awsLambda   = require("node-aws-lambda");

gulp.task('clean', function (cb) {
  del(['./dist', './dist-zip/'], cb);
});

gulp.task('js', function () {
  return gulp.src('src/api/lambda/v1/functions/user/create/index.js')
    .pipe(gulp.dest('dist/'));
});

gulp.task('node-mods', function () {
  return gulp.src('./package.json')
    .pipe(gulp.dest('dist/'))
    .pipe(plugins.install({production: true}));
});

gulp.task('zip', function () {
  return gulp.src(['dist/**/*', '!dist/package.json'])
    .pipe(plugins.zip('dist.zip'))
    .pipe(gulp.dest('./dist-zip'));
});

gulp.task('upload', function (callback) {
  awsLambda.deploy('./dist-zip/dist.zip', require("./src/api/lambda/lambda-config.js"), callback);
});

gulp.task('deploy', function (callback) {
  return runSequence(
    ['clean'],
    ['js', 'node-mods'],
    ['zip'],
    ['upload'],
    callback
  );
});
