document.addEventListener('DOMContentLoaded', function() {
    // Fetch data from APIs
    fetch('http://127.0.0.1:8000/monthly_star')
        .then(response => response.json())
        .then(data => {
            const labels = data.map(item => item.month);
            const starData = data.map(item => item.star);

            // Create line chart for average star ratings
            const starCtx = document.getElementById('starChart').getContext('2d');
            new Chart(starCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '每月平均星等',
                        data: starData,
                        borderColor: 'rgba(241, 227, 126, 1)',
                        backgroundColor: 'rgba(241, 227, 126, 0.2)',
                        fill: true,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '月份'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '星等'
                            },
                            min: 0,
                            max: 5
                        }
                    }
                }
            });
        });

    fetch('http://127.0.0.1:8000/monthly_comment')
        .then(response => response.json())
        .then(data => {
            const labels = data.map(item => item.month);
            const commentData = data.map(item => item.size);

            // Create bar chart for monthly comment count
            const commentCtx = document.getElementById('commentChart').getContext('2d');
            new Chart(commentCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '每月平均文章數',
                        data: commentData,
                        borderColor: 'rgba(135, 178, 61, 1)',
                        backgroundColor: 'rgba(135, 178, 61, 0.5)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '月份'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '文章數'
                            },
                            min: 0
                        }
                    }
                }
            });
        });

    fetch('http://127.0.0.1:8000/monthly_sentiment')
    .then(response => response.json())
    .then(data => {
        const labels = data.map(item => item.month);
        const positiveData = data.map(item => item.positive);
        const negativeData = data.map(item => item.negative);
        const neutralData = data.map(item => item.neutral);

        // Create line chart for sentiment analysis
        const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(sentimentCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '正向情緒',
                        data: positiveData,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: '負向情緒',
                        data: negativeData,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: '中立',
                        data: neutralData,
                        borderColor: 'rgba(148, 148, 148, 1)',
                        backgroundColor: 'rgba(148, 148, 148, 0.2)',
                        fill: false,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '月份'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '情緒總數'
                        },
                        min: 0
                    }
                }
            }
        });
    });

    fetch('http://127.0.0.1:8000/wordcloud')
                .then(response => response.json())
                .then(data => {

                    // list資料，map用來轉換為[word, size]格式
                    const wordData = data.map(item => [item.word, item.size]);

                    console.log('Prepared word data:', wordData); // 除錯

                    WordCloud(document.getElementById('wordcloud'), {
                        list: wordData,
                        gridSize: 8,
                        weightFactor: //調整字的權重大小比例
                        function(size) {
                            return Math.sqrt(size) * 4;
                        },      
                        fontFamily: 'Arial, sans-serif',
                        color: 'random-light',
                        rotateRatio: 0.5,
                        backgroundColor: '#ffffff',
                        shape: 'circle',
                        ellipticity: 1,
                        drawOutOfBound: false,

                    });
                })
                .catch(error => console.error('Error fetching word cloud data:', error));
    
});
