function getPriorDate(date, days_diff) {
    return new Date(date.getTime() - days_diff * 24 * 60 * 60 * 1000)
}

function PieChartCtrl($scope, $http) {
    $scope.pie_data = []
    $scope.google_loaded = false
    $scope.pie_chart = null
    $scope.pie_chart_data = []

    $scope.pieSelectHandler = function() {
        var selection = $scope.pie_chart.getSelection()[0]
        if (selection) {
            $scope.selected_category = $scope.pie_chart_data.getFormattedValue(selection.row, 0)
            $scope.$broadcast('selectedCategory')
        } else {
            $scope.selected_category = null
            $scope.$broadcast('unselectedCategory')
        }
    };

    $scope.drawPieChart = function() {
        if ($scope.pie_data.length == 0 || $scope.google_loaded == false) {
            return
        }
        $scope.pie_chart_data = google.visualization.arrayToDataTable($scope.pie_data);

        var options = {
        title: 'Expenses for ' + $scope.date_from + ' - ' + $scope.date_to + ' period'
        };

        $scope.pie_chart = new google.visualization.PieChart(document.getElementById('pie_chart_div'));
        $scope.pie_chart.draw($scope.pie_chart_data, options);
        google.visualization.events.addListener($scope.pie_chart, 'select', $scope.pieSelectHandler);
    };

    $scope.getData = function() {
        $http.get($scope.data_url, {'params': {'date_from': $scope.date_from, 'date_to': $scope.date_to}}
            ).success(function(data, status, headers, config) {
           $scope.pie_data = data['pie_data'];
           $scope.date_from = data['date_from']
           $scope.date_to = data['date_to']
           $scope.total = data['total']
           $scope.last_rate_date = data['last_rate_date']
        });
        $scope.$broadcast('unselectedCategory')
    };

    $scope.fillDates = function(days_ago) {
        date_to = new Date();
        date_from = getPriorDate(date_to, days_ago);
        $scope.date_from = $.datepicker.formatDate("yy-mm-dd", date_from)
        $scope.date_to = $.datepicker.formatDate("yy-mm-dd", date_to)
        $scope.getData();
    }

    $scope.setCSV = function(element) {
        $scope.csv_file = element.files[0]
    }

    $scope.setDBF = function(element) {
        $scope.dbf_file = element.files[0]
    }

    $scope.submitCSV = function() {
        var form_data = new FormData()
        if (!$scope.csv_file){
            return
        }
        form_data.append("csv_file", $scope.csv_file)
        form_data.append("bank", $scope.bank)
        $scope.sendForm($scope.csv_action, form_data, $('#csv_file'))
    }

    $scope.submitDBF = function() {
        var form_data = new FormData()
        if (!$scope.dbf_file){
            return
        }
        form_data.append("dbf_file", $scope.dbf_file)
        $scope.sendForm($scope.dbf_action, form_data, $('#dbf_file'))
    }

    $scope.sendForm = function(url, form_data, file_el) {
        var o_req = new XMLHttpRequest();
        o_req.open("POST", url, true);
        o_req.onload = function(oEvent) {
            if (o_req.status == 200) {
              file_el.val('')
              $scope.getData();
            } else {
                console.log("Error " + o_req.status + " occurred uploading your file.");
            }
        };
        o_req.send(form_data);
    }

    $scope.$watch('google_loaded', function(newValue, oldValue) {
        $scope.drawPieChart();
    });
    $scope.$watch('pie_data', function(newValue, oldValue) {
        $scope.drawPieChart();
    });
}

PieChartCtrl.$inject = ['$scope', '$http'];


function CategoryCtrl($scope, $http) {
    $scope.category = null
    $scope.rows = []
    $scope.show_details = false
    $scope.category_chart_data = []
    $scope.column_data = []
    $scope.column_chart = null

    $scope.$on('selectedCategory', function(event) {
        $http.get($scope.category_url,
            {'params':
               {
                category: event.targetScope.selected_category,
                date_from: $scope.date_from,
                date_to: $scope.date_to
               }
           }).success(function(data, status, headers, config) {
                $scope.updateCategory(data);
               })
    });

    $scope.$on('unselectedCategory', function(event) {
        $scope.show_details = false;
        if(!$scope.$$phase) {
            $scope.$apply();
        }
    });

    $scope.updateCategory = function(data) {
        $scope.rows = []
        var column_chart_data = [];
        for (var key in data) {
            var row = data[key];
            row['date'] = $.datepicker.parseDate("yy-mm-dd", row['date'])
            row['amount'] = parseFloat(row['amount'])
            row['description'] = row['description'].substring(0,80)
            $scope.rows.push(row)
            column_chart_data.push([row['date'], row['amount']]);
        }
        $scope.category_chart_data = $scope.groupByMonth(column_chart_data);
        $scope.show_details = true
    }

    $scope.groupByMonth = function(data) {
        buckets = {}
        result = []
        for (var key in data) {
            var date = data[key][0];
            var bkey = new Date(date.getFullYear(), date.getMonth(), 1);
            if (!buckets[bkey]) {
                buckets[bkey] = [bkey, data[key][1]];
            } else {
                buckets[bkey][1] += data[key][1];
            }
        }
        for (var bkey in buckets) {
            if (buckets.hasOwnProperty(bkey)) {
                result.push(buckets[bkey]);
            }
        }
        return result
    }

    $scope.$watch('category_chart_data', function(column_chart_data) {
        if ($scope.category_chart_data.length==0) {
            return
        }
        // var data = google.visualization.arrayToDataTable(data);
        $scope.column_data = new google.visualization.DataTable();
        $scope.column_data.addColumn('date', 'Date');
        $scope.column_data.addColumn('number', 'Amount');
        $scope.column_data.addRows(column_chart_data);

        var formatter_short = new google.visualization.DateFormat({formatType: 'short'});
        formatter_short.format($scope.column_data, 0);

        $scope.column_chart = new google.visualization.ColumnChart(document.getElementById('column_chart_div'));
        $scope.column_chart.draw($scope.column_data, {'chartArea.width': 500});
        google.visualization.events.addListener($scope.column_chart, 'select', $scope.columnSelectHandler);
    })

    $scope.columnSelectHandler = function() {
        var selection = $scope.column_chart.getSelection()[0];
        if (selection) {
            var selected_month = $scope.column_data.getFormattedValue(selection.row, 0);
            date = $.datepicker.parseDate("dd.mm.yy", selected_month);

            for (var key in $scope.rows) {
                row = $scope.rows[key]
                // var bkey = new Date(date.getFullYear(), date.getMonth(), 1);
                if (row['date'].getFullYear() == date.getFullYear() &&
                    row['date'].getMonth() == date.getMonth()) {
                    row['bold'] = true;
                } else {
                    row['bold'] = false;
                }
            }
        } else {
            for (var key in $scope.rows) {
                row['bold'] = false;
            }
        }
        if(!$scope.$$phase) {
            $scope.$apply();
        }
    }
}

CategoryCtrl.$inject = ['$scope', '$http'];
