// https://codesandbox.io/s/o29j95wx9
new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    ingredients: [],
    product_lines: [],
    loading: false,
    currentIngredient: {},
    message: null,
    page: 1,
    perPage: 10,
    pages: [],
    newIngredient: { 'ingredient_name': '', 'id': 0, 'description': null, 'package_size': '', 'cpp': 0, 'comment': null, },
    ingredientFile: null,
    search_term: '',
    search_input: '',
    has_paginated: false,
    csv_uploaded: false,
    disable_paginate: false,
    // sorting variables
    sortKey: 'ingredient_name',
    sortAsc: [
      {'id': true},
      { 'ingredient_name': true },
      { 'package_size': true },
      { 'cpp': true },
      { 'description': true },
      { 'id': true }
    ],
    // File Upload Errors
    upload_errors: '',
    name_error: '',
    error:'',
    unit_error: '',
  },
  mounted: function () {
    this.getIngredients();
    $("#search_input").autocomplete({
      minLength: 1,
      delay: 100,
      // https://stackoverflow.com/questions/9656523/jquery-autocomplete-with-callback-ajax-json
      source: function (request, response) {
        $.ajax({
          url: "/api/ingredient",
          dataType: "json",
          data: {
            // attach '?search=request.term' to the url 
            search: request.term
          },
          success: function (data) {
            ingr_names = $.map(data, function (item) {
              return [item.ingredient_name];
            })
            response(ingr_names);
          }
        });
      },
      messages: {
        noResults: '',
        results: function() {}
      }
    });
  },
  methods: {
    getIngredients: function () {
      
    },
    getIngredient: function (id) {

    },
    deleteIngredient: function (id) {

    },
    addIngredient: function () {

    },
    updateIngredient: function () {

    },
    getProductLines: function(){
      let api_url = '/api/product_line/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                    this.product_lines = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
    },
    updateProductLines: function(event) {
      let api_url = '/api/bulk_match_manufacturing_lines/';
        let active_pls = this.product_lines.filter((pl) => {
          return pl['all_active'];
        }).map((pl) => {
          return pl['pl_short_name'];
        })
        let request = {
          'active_pl_short_names': active_pls
        }
        this.$http.post(api_url, request)
        .then((response) => {
          $("#updatePLModal").modal('hide');
        })
        .catch((err) => {
            console.log(err);
        })
      },
      postCustomer: function(){
        let api_url = 'api/customers/'
        var e = document.getElementById("customers");
        var text = e.options[e.selectedIndex].text;
        let request = text;
        this.$http.post(api_url, request)
        .then((response) => {
          this.product_lines = response.data;
        })
        .catch((err) => {
            console.log(err);
        })
      }

      // disablePage: function(){
      //   this.disable_paginate = true;
      // },
   
      // ml_checkbox_click: function(ev, ml) {
      //   ml['part_active'] = false;
      // },
    // setPages: function () {
    //   let numberOfPages = Math.ceil(this.ingredients.length / this.perPage);
    //   for (let index = 1; index <= numberOfPages; index++) {
    //     this.pages.push(index);
    //   }
    // },
    // addPage: function () {
    //   this.pages.push(Math.ceil(this.ingredients.length / this.perPage) + 1);
    // },
    // deletePage: function () {
    //   this.pages = [];
    //   let numberOfPages = Math.ceil(this.ingredients.length / this.perPage);
    //   for (let index = 1; index < numberOfPages; index++) {
    //     this.pages.push(index);
    //   }
    // },
    // paginate: function (ingredients) {
    //   let page = this.page;
    //   // console.log(page)
    //   let perPage = this.perPage;
    //   let from = (page * perPage) - perPage;
    //   let to = (page * perPage);
    //   return ingredients.slice(from, to);
    // },
    // https://www.academind.com/learn/vue-js/snippets/image-upload/

    exportCSV: function () {
      
    },

    // Trigger an action to update search_term
    // Dirty trick to get around a VueJS bug: https://github.com/vuejs/vue/issues/5248 
    onBlur: function (event) {
      if (event && this.search_term !== event.target.value)
        this.search_term = event.target.value
    },

    getSkus: function (ingredientid) {
      this.loading = true;
      this.$http.get('/api/skus_to_ingredient/' + ingredientid)
        .then((response) => {
          this.skus = response.data;
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          console.log(err);
        })
    },

    // https://vuejs.org/v2/guide/migration.html#Replacing-the-orderBy-Filter
    sortBy: function (key) {
      this.sortKey = key
      this.sortAsc[key] = !this.sortAsc[key]
      if (!this.sortAsc[this.sortKey]) {
        this.ingredients = _.sortBy(this.ingredients, this.sortKey)
      } else {
        this.ingredients = _.sortBy(this.ingredients, this.sortKey).reverse()
      }
    },

    // disablePage: function(){
    //     this.disable_paginate = true;
    //   },

  },

  // computed: {
  //   // is pagination necessary though?
  //   displayedIngredients() {
  //     var x = document.getElementById("pagination");
  //     if(this.disable_paginate){
  //         x.style.display = "none";
  //       return this.ingredients;
  //     } else{
  //       x.style.display = "block";
  //        return this.paginate(this.ingredients);
  //   }
  //   }
  // },


});