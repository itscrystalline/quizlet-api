async function quizlet(id) {
    let res = await fetch(`https://quizlet.com/webapi/3.4/studiable-item-documents?filters%5BstudiableContainerId%5D=${id}&filters%5BstudiableContainerType%5D=1&perPage=500&page=1`).then(res => res.json())
    let currentLength = res.responses[0].models.studiableItem.length;
    let token = res.responses[0].paging.token
    let terms = res.responses[0].models.studiableItem;
    let page = 2;
    while (currentLength >= 500) {
        let res = await fetch(`https://quizlet.com/webapi/3.4/studiable-item-documents?filters%5BstudiableContainerId%5D=${id}&filters%5BstudiableContainerType%5D=1&perPage=500&page=${page++}&pagingToken=${token}`).then(res => res.json());
        terms.push(...res.responses[0].models.studiableItem);
        currentLength = res.responses[0].models.studiableItem.length;
        token = res.responses[0].paging.token;
    }
    let json = {
        pools: []
    }
    let pool = {
        id: id,
        length: terms.length,
        cards: []
    }
    for (var i = 0; i < terms.length; i++) {
        const card = {
            side1: terms[i].cardSides[0].media[0].plainText,
            side2: terms[i].cardSides[1].media[0].plainText
        };
        pool.cards.push(card);
    }
    json.pools.push(pool);

    return json;
}

quizlet(process.argv[2]).then(r => console.log(JSON.stringify(r)));