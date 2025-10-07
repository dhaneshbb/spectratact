export default [
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      'release/**',
      'coverage/**',
      '.bkup/**',
      'src/spectratact/**'
    ]
  },
  {
    files: ['src/desktop/modules/*.js', 'src/desktop/desktop-app.js'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      globals: {
        console: 'readonly',
        process: 'readonly',
        document: 'readonly',
        window: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        setImmediate: 'readonly',
        localStorage: 'readonly',
        getComputedStyle: 'readonly',
        performance: 'readonly',
        Buffer: 'readonly'
      }
    },
    rules: {
      'indent': 'off',
      'quotes': ['warn', 'single'],
      'semi': ['warn', 'always'],
      'no-unused-vars': ['warn'],
      'no-console': 'off',
      'no-undef': 'error'
    }
  },
  {
    files: ['src/desktop/**/*.js', 'test/frontend/**/*.js'],
    ignores: ['src/desktop/modules/*.js', 'src/desktop/desktop-app.js'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'commonjs',
      globals: {
        console: 'readonly',
        process: 'readonly',
        __dirname: 'readonly',
        require: 'readonly',
        module: 'readonly',
        exports: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        setImmediate: 'readonly',
        Buffer: 'readonly',
        URL: 'readonly',
        jest: 'readonly',
        describe: 'readonly',
        test: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly'
      }
    },
    rules: {
      'indent': 'off',
      'quotes': ['warn', 'single'],
      'semi': ['warn', 'always'],
      'no-unused-vars': ['warn'],
      'no-console': 'off',
      'no-undef': 'error'
    }
  }
];
