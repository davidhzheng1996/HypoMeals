var starting = new Vue({
    el: '#starting',
    delimiters: ['${', '}'],
    data: {
        manufacturing_lines: new Set(),
        scheduled_goals: [], 
        manufacture_lines: [],
        skus: [],  
        ingredients: [], 
        // {sku_name, ingredient_name, goal_name, case_quantity, start_time, end_time, duration(hrs)}
        report_items: [],    
        // manufacturing lines
        // groups: new vis.DataSet(),
        // // skus
        // items: new vis.DataSet(),
        search_term: '',
        message: ''
    },
    methods: {
        getItems: function (userid) {
            let api_url = '/api/scheduler_report/';
      // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
      //console.log(this.search_term);
      this.loading = true;
      this.$http.get(api_url)
        .then((response) => {
          this.skus = response.data;
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          console.log(err);
        })
        },
    },
    mounted: function () {
        
    }
});

// 
//  var items = new vis.DataSet([
//     {id: 1, content: 'item 1', start: '2013-04-20'},
//     {id: 2, content: 'item 2', start: '2013-04-14'},
//     {id: 3, content: 'item 3', start: '2013-04-18'},
//     {id: 4, content: 'item 4', start: '2013-04-16', end: '2013-04-19'},
//     {id: 5, content: 'item 5', start: '2013-04-25'},
//     {id: 6, content: 'item 6', start: '2013-04-27'}
//   ]);

// create a Timeline

// function handleDragEnd(event) {
//     // Last item that just been dragged, its ID is the same of event.target
//     var newItem_dropped = timeline1.itemsData.get(event.target.id);

//     var html = "<b>id: </b>" + newItem_dropped.id + "<br>";
//     html += "<b>content: </b>" + newItem_dropped.content + "<br>";
//     html += "<b>start: </b>" + newItem_dropped.start + "<br>";
//     html += "<b>end: </b>" + newItem_dropped.end + "<br>";
//     document.getElementById('output').innerHTML = html;
// }

// var items = document.querySelectorAll('.items .item');


// for (var i = items.length - 1; i >= 0; i--) {
//     var item = items[i];
//     item.addEventListener('dragstart', handleDragStart.bind(this), false);
// }


