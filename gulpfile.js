'use strict';

const path = require('path');

const { src, pipe, dest, series, parallel, watch } = require('gulp');
const Fiber = require('fibers');
const rollup = require('rollup');
const rollupPluginCommonjs = require('@rollup/plugin-commonjs');
const rollupPluginNodeResolve = require('@rollup/plugin-node-resolve');
const rollupPluginTerser = require('rollup-plugin-terser').terser;

const plugins = {}
plugins.sass = require('gulp-sass');
plugins.gulpStylelint = require('gulp-stylelint');
plugins.gulpif = require('gulp-if');
plugins.postcss = require('gulp-postcss');

const paths = {
  src: 'src/assets/',
  node_modules: 'node_modules/',
  dist: 'dist/alerts/assets/',
  govuk_frontend: 'node_modules/govuk-frontend/',
  assetsUrl: '/alerts/assets/'
};

plugins.sass.compiler = require('sass');

const copy = {
  govuk_frontend: {
    fonts: () => {
      return src(paths.govuk_frontend + 'govuk/assets/fonts/**/*')
        .pipe(dest(paths.dist + 'fonts/'));
    },
    images: () => {
      return src(paths.govuk_frontend + 'govuk/assets/images/**/*')
        .pipe(dest(paths.dist + 'images/'));
    }
  },
  html5shiv: () => {
    return src(paths.node_modules + 'html5shiv/dist/*.min.js')
      .pipe(dest(paths.dist + 'javascripts/vendor/html5shiv/'));
  },
  images: () => {
      return src(paths.src + 'images/**/*')
        .pipe(dest(paths.dist + 'images/'));
  }
};

const javascripts = {
  details: () => {
    // Use Rollup to combine all JS in JS module format into a Immediately Invoked Function
    // Expression (IIFE) to:
    // - deliver it in one bundle
    // - allow it to run in browsers without support for JS Modules
    return rollup.rollup({
      input: paths.src + 'javascripts/govuk-frontend-details.mjs',
      plugins: [
        // determine module entry points from either 'module' or 'main' fields in package.json
        rollupPluginNodeResolve.nodeResolve({
          mainFields: ['module', 'main']
        }),
        // gulp rollup runs on nodeJS so reads modules in commonJS format
        // this adds node_modules to the require path so it can find the GOVUK Frontend modules
        rollupPluginCommonjs({
          include: 'node_modules/**'
        }),
        // Terser is a replacement for UglifyJS
        rollupPluginTerser()
      ]
    }).then(bundle => {
      return bundle.write({
        file: paths.dist + 'javascripts/govuk-frontend-details.js',
        format: 'iife',
        name: 'GOVUK',
        sourcemap: true
      });
    });
  },
  sharingButton: () => {
    // Use Rollup to combine all JS in JS module format into a Immediately Invoked Function
    // Expression (IIFE) to:
    // - deliver it in one bundle
    // - allow it to run in browsers without support for JS Modules
    return rollup.rollup({
      input: paths.src + 'javascripts/sharing-button-init.mjs',
      plugins: [
        // determine module entry points from either 'module' or 'main' fields in package.json
        rollupPluginNodeResolve.nodeResolve({
          mainFields: ['module', 'main']
        }),
        // gulp rollup runs on nodeJS so reads modules in commonJS format
        // this adds node_modules to the require path so it can find the GOVUK Frontend modules
        rollupPluginCommonjs({
          include: 'node_modules/**'
        }),
        // Terser is a replacement for UglifyJS
        rollupPluginTerser()
      ]
    }).then(bundle => {
      return bundle.write({
        file: paths.dist + 'javascripts/sharing-button.js',
        format: 'iife',
        name: 'GOVUK',
        sourcemap: true
      });
    });
  },
  relativeDates: () => {
    // Use Rollup to combine all JS in JS module format into a Immediately Invoked Function
    // Expression (IIFE) to:
    // - deliver it in one bundle
    // - allow it to run in browsers without support for JS Modules
    return rollup.rollup({
      input: paths.src + 'javascripts/relative-dates-init.mjs',
      plugins: [
        // determine module entry points from either 'module' or 'main' fields in package.json
        rollupPluginNodeResolve.nodeResolve({
          mainFields: ['module', 'main']
        }),
        // gulp rollup runs on nodeJS so reads modules in commonJS format
        // this adds node_modules to the require path so it can find the GOVUK Frontend modules
        rollupPluginCommonjs({
          include: 'node_modules/**'
        })
      ]
    }).then(bundle => {
      return bundle.write({
        file: paths.dist + 'javascripts/relative-dates.js',
        format: 'iife',
        name: 'GOVUK',
        sourcemap: true
      });
    });
  }
};

const scss = {
  compile: () => {
    return src(paths.src + 'stylesheets/**/*.scss')
      .pipe(plugins.sass(
        {
          fiber: Fiber,
          includePaths: [paths.govuk_frontend],
          outputStyle: 'compressed'
        })
        .on('error', plugins.sass.logError))
        .pipe(plugins.gulpif(
          (file) => {
            return path.basename(file.path) === 'main-ie8.css';
          },
          plugins.postcss([require('oldie')()])
        ))
      .pipe(dest(paths.dist + 'stylesheets/'));
  }
};

const defaultTask = parallel(
  copy.govuk_frontend.fonts,
  copy.govuk_frontend.images,
  copy.html5shiv,
  copy.images,
  scss.compile,
  javascripts.details,
  javascripts.sharingButton,
  javascripts.relativeDates
);

exports.default = defaultTask;
