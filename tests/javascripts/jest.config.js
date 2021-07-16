module.exports = {
  testEnvironment: "jsdom",
  transform: {
    ".*\.js$": "rollup-jest"
  },
  setupFiles: ['./support/setup.js']
}
