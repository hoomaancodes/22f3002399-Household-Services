// Vue CLI 4.x configuration
module.exports = {
  publicPath: '/',
  filenameHashing: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  pages: {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: 'Household Services Application'
    }
  },
  // Add chainWebpack configuration to prevent HTML plugin conflicts
  chainWebpack: config => {
    // Remove the default HtmlWebpackPlugin instance completely
    // to prevent conflicts with our pages configuration
    config.plugins.delete('html')
    config.plugins.delete('preload')
    config.plugins.delete('prefetch')
  }
}
