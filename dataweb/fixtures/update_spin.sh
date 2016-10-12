#curl -i -X GET "http://localhost:8080/rdf4j-server/repositories/profiles-test/rdf-graphs/service?graph=cobweb:Species_GBIF_qbdimension"
# curl -i -X DELETE "http://localhost:8080/rdf4j-server/repositories/profiles-test/contexts"
FILES=`ls ../static/*.ttl  | sed -e 's/...static.//'`
#FILES=cube.ttl
for f in $FILES
do
	echo $f
	curl -iX POST -T "../static/$f" -H "Content-Type: application/x-turtle;charset=UTF-8" "http://localhost:8080/rdf4j-server/repositories/profiles-test/rdf-graphs/service?graph=%3Cfile://$f%3E" 
done

