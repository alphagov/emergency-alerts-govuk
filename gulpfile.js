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
plugins.hash = require('gulp-sha256-filename');
plugins.rename = require('gulp-rename');
plugins.clean = require('gulp-clean');


const paths = {
  src: 'src/assets/',
  node_modules: 'node_modules/',
  dist: 'dist/alerts/assets/',
  govuk_frontend: 'node_modules/govuk-frontend/',
  assetsUrl: '/alerts/assets/'
};

const filenameFormat = '{name}-{hash:8}{ext}'

plugins.sass.compiler = require('sass');

const copy = {
  govuk_frontend: {
    fonts: () => {
      return src(paths.govuk_frontend + 'govuk/assets/fonts/**/*')
        .pipe(dest(paths.dist + 'fonts/'));
        // Fonts have their own filename hash so we don’t need to add
        // our own
    },
    images: () => {
      return src(paths.govuk_frontend + 'govuk/assets/images/**/*')
        .pipe(dest(paths.dist + 'images/'))
        .pipe(plugins.hash(filenameFormat))
        .pipe(dest(paths.dist + 'images/'));
    }
  },
  html5shiv: () => {
    return src(paths.node_modules + 'html5shiv/dist/*.min.js')
      .pipe(dest(paths.dist + 'javascripts/vendor/html5shiv/'))
      .pipe(plugins.hash(filenameFormat))
      .pipe(dest(paths.dist + 'javascripts/vendor/html5shiv/'));
  },
  images: () => {
      return src(paths.src + 'images/**/*')
        .pipe(dest(paths.dist + 'images/'))
        .pipe(plugins.hash(filenameFormat))
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
      input: {
        'govuk-frontend-details': paths.src + 'javascripts/govuk-frontend-details-init.mjs'
      },
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
        dir: paths.dist + 'javascripts/',
        entryFileNames: '[name]-[hash].js',
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
      input: {
        'sharing-button': paths.src + 'javascripts/sharing-button-init.mjs'
      },
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
        dir: paths.dist + 'javascripts/',
        entryFileNames: '[name]-[hash].js',
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
      input: {
        'relative-dates': paths.src + 'javascripts/relative-dates-init.mjs'
      },
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
        dir: paths.dist + 'javascripts/',
        entryFileNames: '[name]-[hash].js',
        format: 'iife',
        name: 'GOVUK',
        sourcemap: true
      });
    });
  }
};

const restoreOriginalJavascriptFiles = () => src(
  paths.dist + 'javascripts/*.js*'
)
  .pipe(
    plugins.rename(path => {
      return {
        dirname: path.dirname,
        basename: path.basename.replace(/(.*)-([a-f0-9]{8})([\.js]?)$/i, '$1$3'),
        extname: path.extname
      }
    })
  )
  .pipe(dest(paths.dist + 'javascripts/'));

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
      .pipe(dest(paths.dist + 'stylesheets/'))
      .pipe(plugins.hash())
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
