// https://codesandbox.io/s/o29j95wx9
var vm = new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    product_lines: [],
    customers: [],
    items:{},
    loading: false,
    message: null,
    selected_customer: '',
    page: 1,
    perPage: 10,
    pages: [],
    timespan: {'start_date':'','end_date':''},
    ingredientFile: null,
    search_term: '',
    search_input: '',
    request_dict: {},
    has_paginated: false,
    csv_uploaded: false,
    disable_paginate: false,
    // sorting variables
    // File Upload Errors
    upload_errors: '',
    name_error: '',
    error:'',
    unit_error: '',
  },
  mounted: function () {
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
    getItems: function (skuid) {
      // var span = this.updateTimespan();
      // console.log(span)
      this.loading = true;
      this.request_dict['timespan'] = this.timespan;
      console.log(this.selected_customer)
       this.request_dict['customer'] = this.selected_customer;
       console.log(this.request_dict)
           this.$http.post('/api/get_sku_drilldown/'+skuid, this.request_dict)
               .then((response) => {
                   this.items = response.data;
                   console.log(this.items)
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
          this.$http.get('../api/get_customer')
            .then((response) => {
              this.customers = response.data;
              //this.getItems();
            })
            .catch((err) => {
                console.log(err);
            })
    },
      // getCustomer: function(){
      //   this.$http.get('../api/get_customer')
      //       .then((response) => {
      //         this.customers = response.data;
      //         //this.getItems();
      //       })
      //       .catch((err) => {
      //           console.log(err);
      //       })
      //   return;
      // },
      postCustomer: function(){
        // let api_url = 'api/customers/'
        // var e = document.getElementById("customers");
        // var text = e.options[e.selectedIndex].text;
        // let request = text;
        // this.$http.post(api_url, request)
        // .then((response) => {
        //   this.product_lines = response.data;
        // })
        // .catch((err) => {
        //     console.log(err);
        // })
      },
      getLineGraph: function(){

      },
      getSelected: function(event){
        this.selected_customer = event.target.value;
        this.getItems(savedSkuId);
      },
      updateTimespan: function(){
        $("#TimeSpanModal").modal('hide');
        this.getItems(savedSkuId);
      },
    // https://www.academind.com/learn/vue-js/snippets/image-upload/

    exportCSV: function () {
      
    },

    // Trigger an action to update search_term
    // Dirty trick to get around a VueJS bug: https://github.com/vuejs/vue/issues/5248 
    onBlur: function (event) {
      if (event && this.search_term !== event.target.value)
        this.search_term = event.target.value
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