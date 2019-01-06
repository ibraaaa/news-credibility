# Arabic News Credibility Assessment project.

Please cite the following paper in your project/publication ... etc. if you'll make use of the dataset or any part of the code:
```
@inproceedings{hammad2013automating,
  title={Automating Credibility Assessment of Arabic News},
  author={Hammad, Mohamed and Hemayed, Elsayed},
  booktitle={International Conference on Social Informatics},
  pages={139--152},
  year={2013},
  organization={Springer}
}
```
## Project Description:

1. Arabic News dataset; described in details below.
2. A number positive/negative label(s) assigned for each article by a service called MCE Watch. The service used to operate at the of this project and assigns grading for each article across different dimension. The service was human operated.
3. Source code for crawling and parsing both the news sites and MC Watch.
4. Source code for the classification software.

## Dataset Description
This project includes an Arabic News dataset of around 10,000 articles from 2013. The articles were crawled from 15 different news sites, namely:

1. Akhbar El-Yom
2. Alahram
3. Almasry El Yom
4. BBC Arabic
5. CNN Arabic
6. El Dostor News
7. El fagr
8. El Watan News
9. English Ahram
10. English Freedom and Justice Party
11. Freedom and Justice Party
12. Masrawy
13. Official Youm 7
14. Shorouk News
15. Tahrir News Official

All articles were parsed to extract the text from the HTML pages. The first line in the text file always corresponds to the article's title. The remaining text corresponds to the article's body.

More details can be found in the publication or feel free to reach out to the author(s).
