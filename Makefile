setup:
	./setup_env.sh

pages:
	./build.sh dayu haowen 0.0.1 https://github.com/jcold/youlog-press.git "haowen@v0.0.1" haowen

youlog:
	./make_gz.sh dayu haowen 0.0.1 /Users/dayu/tmp/cicd/src/haowen/__everkm/dist

all-in-one:
	make setup
	make pages
	make youlog