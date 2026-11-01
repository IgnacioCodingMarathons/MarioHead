from __future__ import annotations

import argparse
import csv
import random
import re
import unicodedata
from pathlib import Path

FEATURE_COUNT = 14
MODEL_PATH = Path(__file__).resolve().parent / "assets" / "jokeeval.onnx"
JOKE_NOUNS = (
    "penguin", "duck", "fish", "frog", "cat", "dog", "elephant", "bear",
    "rabbit", "mouse", "owl", "bee", "cow", "pig", "horse", "turtle",
    "snake", "shark", "monkey", "squirrel", "robot", "pirate", "astronaut",
    "teacher", "doctor", "baker", "chef", "ghost", "vampire", "snowman",
    "banana", "potato", "pizza", "sandwich", "shoe", "umbrella", "phone",
    "clock", "book", "lamp", "fridge", "spoon", "suitcase", "mailbox",
    "door", "cloud", "moon", "volcano", "bicycle", "calendar", "computer",
    "scarecrow", "tomato", "pencil",
)
CONNECTIVES = {
    "although", "because", "but", "except", "however", "instead", "since",
    "so", "therefore", "then", "though", "until", "when", "while",
    "ademas", "aunque", "asi", "como", "cuando", "despues", "entonces",
    "pero", "porque", "por", "pues", "sin", "tambien", "entretanto",
    "mas", "portanto", "quando", "tambem", "todavia", "contudo",
}
HUMOR_CUES = {
    "absurd", "banana", "because", "chicken", "cross", "dad", "funny",
    "joke", "knock", "laugh", "pun", "road", "side", "why", "what", "how",
    "broma", "chiste", "gracioso", "risa", "pollo", "gallina", "cruzar",
    "camino", "carretera", "piada", "engracado", "rir", "galinha", "frango",
    "atravessar", "estrada", "por", "que", "como", "qual", "quien", "quem",
    "abeja", "zum", "techo", "vaca", "concentrada", "matematicas", "problema",
    "libro", "pato", "huevo", "zero", "cinto", "tomate", "extrato", "pato",
    "queijo", "piao", "banco", "pave", "piada",
    "penguin", "penguins", "pinguino", "pingüino", "duck", "fish", "frog",
    "cat", "dog", "elephant", "bear", "rabbit", "mouse", "owl", "bee",
    "cow", "pig", "horse", "turtle", "snake", "shark", "monkey", "squirrel",
    "robot", "pirate", "astronaut", "teacher", "doctor", "baker", "chef",
    "ghost", "vampire", "snowman", "potato", "pizza", "sandwich", "shoe",
    "umbrella", "phone", "clock", "book", "lamp", "fridge", "spoon", "suitcase",
    "mailbox", "door", "cloud", "moon", "volcano", "ice", "cold", "waddle",
    "beak", "flight", "fly", "chilly", "pato", "peixe", "sapo", "gato", "cachorro",
    "elefante", "urso", "coelho", "rato", "coruja", "porco", "cavalo", "tartaruga",
    "cobra", "tubarao", "macaco", "pingüim", "pingui", "pinguino", "pato", "pez",
    "rana", "perro", "oso", "conejo", "raton", "buho", "cerdo", "caballo", "tortuga",
    "serpiente", "tiburon", "mono", "hielo", "frio", "pico", "volar", "pinguim",
}
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "for", "from", "he", "her", "his", "i", "in", "is", "it", "its",
    "of", "on", "or", "our", "she", "so", "that", "the", "their",
    "they", "this", "to", "was", "we", "were", "with", "you", "your",
    "al", "algo", "como", "con", "de", "del", "el", "ella", "ellas",
    "ellos", "en", "es", "esta", "este", "la", "las", "lo", "los", "me",
    "mi", "muy", "no", "nos", "o", "para", "por", "que", "se", "ser",
    "si", "su", "sus", "un", "una", "unos", "unas", "y", "yo",
    "ainda", "as", "com", "da", "das", "do", "dos", "e", "ela", "elas",
    "ele", "eles", "em", "eu", "foi", "mais", "na", "nas", "nem", "no",
    "nos", "os", "ou", "pelo", "pela", "pelos", "pelas", "seu", "sua",
    "um", "uma", "voce", "voces",
}
def _normalized_word(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.casefold())
    return "".join(character for character in decomposed
                   if unicodedata.category(character) != "Mn")


def extract_features(text: str) -> list[float]:
    words = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)*", text, flags=re.UNICODE)
    lowered = [_normalized_word(word) for word in words]
    count = len(words)
    unique = set(lowered)
    sentences = [part for part in re.split(r"[.!?]+", text) if part.strip()]
    content = [word for word in lowered if word not in STOP_WORDS]
    content_unique = set(content)
    repetition = (count - len(unique)) / max(1, count)
    adjacent_repeat = sum(a == b for a, b in zip(lowered, lowered[1:])) / max(1, count - 1)
    connectors = sum(word in CONNECTIVES for word in lowered)
    humor = sum(word in HUMOR_CUES for word in lowered)
    grammar = 0.0
    if count:
        grammar = (
            0.2 * float(text.lstrip()[:1].isupper())
            + 0.2 * float(text.rstrip().endswith((".", "!", "?")))
            + 0.2 * float(text.count("(") == text.count(")"))
            + 0.2 * float(text.count('"') % 2 == 0)
            + 0.2 * float(not any(pattern in " " + " ".join(lowered) + " " for pattern in (
                " i is ", " they is ", " we was ", " he are ", " she are ",
                " a apple ", " an banana ", " yo es ", " ellos es ", " nosotros fue ",
                " el manzana ", " la problema ", " eles e ", " nos foi ", " eu esta ",
                " um banana ", " uma problema ",
            )))
        )
    if len(sentences) < 2:
        cohesion = 0.65 if count else 0.0
    else:
        sentence_words = [
            {_normalized_word(word) for word in re.findall(
                r"[^\W\d_]+(?:['’][^\W\d_]+)*", sentence, flags=re.UNICODE
            ) if _normalized_word(word) not in STOP_WORDS}
            for sentence in sentences
        ]
        overlap = []
        for left, right in zip(sentence_words, sentence_words[1:]):
            overlap.append(len(left & right) / max(1, len(left | right)))
        cohesion = min(1.0, 0.35 + 0.55 * (sum(overlap) / max(1, len(overlap)))
                       + 0.1 * min(1.0, connectors / 2))
    setup = float(
        ("?" in text or "¿" in text)
        and any(word in lowered for word in (
            "why", "what", "how", "que", "como", "cual", "quien", "quem",
            "qual", "porque",
        ))
    )
    return [
        min(1.0, len(text) / 240),
        min(1.0, count / 40),
        min(1.0, (sum(map(len, words)) / max(1, count)) / 10),
        min(1.0, len(sentences) / 5),
        len(unique) / max(1, count),
        repetition,
        min(1.0, connectors / 4),
        grammar,
        cohesion,
        min(1.0, humor / 3),
        setup,
        float(bool(count) and text.rstrip().endswith((".", "!", "?"))),
        float(bool(count) and text.lstrip()[:1].isupper()),
        adjacent_repeat,
    ]




def weak_rating(features: list[float]) -> float:
    word_ratio = features[1]
    length_fit = max(0.0, 1.0 - abs(word_ratio - 0.45) / 0.55)
    value = (
        0.4 + 1.4 * length_fit + 1.8 * features[7] + 2.0 * features[8]
        + 1.6 * features[9] + 0.9 * features[4] + 0.7 * features[6]
        + 0.8 * features[10] - 1.5 * features[5] - 1.2 * features[13]
    )
    return max(0.0, min(10.0, value))


def synthetic_examples() -> list[tuple[str, float]]:
    setups = [
        "Why did the {a} {action} the {b}?",
        "Why was the {a} feeling {mood}?",
        "What did the {a} say to the {b}?",
        "Why did the {a} bring a {b}?",
    ]
    punchlines = [
        "Because it wanted to {ending}.",
        "Because it was {ending}.",
        "It said, '{ending}!'",
        "Then it {ending} instead.",
    ]
    nouns = list(JOKE_NOUNS)
    actions = [
        "visit", "avoid", "carry", "call", "follow", "thank", "wear", "read",
        "paint", "build", "borrow", "invite", "catch", "bring", "meet", "teach",
    ]
    endings = [
        "stay in its lane", "make a good point", "turnip the volume", "get a little byte",
        "be outstanding in its field", "draw attention", "keep its days numbered",
        "take a break", "go with the flow", "keep things rolling",
        "break the ice", "make a splash", "get a little chilly", "find its other half",
        "turn over a new leaf", "keep its cool", "get the last word", "make a scene",
        "go bananas", "be a little bouncy", "put its best foot forward",
    ]
    examples = []
    chicken_jokes = [
        "Why did the chicken cross the road? To get to the other side.",
        "Why did the chicken cross the road? Because it wanted to get to the other side.",
        "Why did the chicken cross the road? To prove it wasn't chicken.",
        "Why did the chicken cross the road? It saw the other side and got curious.",
        "Why did the chicken cross the road? Because the other side had better snacks.",
        "Why did the chicken cross the road? To show the possum it could be done.",
        "Why did the chicken cross the road? It wanted to get to the shell station.",
        "Why did the chicken cross the road? The road was moving, and it wanted to keep up.",
        "Why did the chicken cross the playground? To get to the other slide.",
        "Why did the chicken cross the basketball court? It heard the referee was blowing fouls.",
        "Why did the chicken cross the library? It wanted to check out the other side.",
        "Why did the chicken cross the internet? To get to the other site.",
        "Why did the penguin bring a suitcase? It was going on an ice trip.",
        "Why don't penguins like talking to strangers? They find the ice breakers awkward.",
        "What do penguins wear on their heads? Ice caps.",
        "Why did the penguin cross the road? To get to the chilly side.",
        "Why was the penguin a good comedian? It always had a cool delivery.",
        "What is a penguin's favorite relative? Aunt Arctica.",
        "Why did the penguin bring a fish to the party? It wanted to break the ice.",
        "How do penguins build houses? Igloos it together.",
        "Why did the penguin sit on the clock? It wanted to be on time for the ice age.",
        "What do you call a penguin in the desert? Lost.",
        "Why did the penguin open a bakery? It was great at making chill-dough.",
        "Why did the duck bring a suitcase? It was ready to go on a quack-cation.",
        "Why did the computer go to the doctor? It caught a virus.",
        "Why did the bicycle fall over? It was two tired.",
        "What do you call a bear with no teeth? A gummy bear.",
        "Why did the scarecrow win an award? It was outstanding in its field.",
        "What did the ocean say to the beach? Nothing, it just waved.",
        "Why did the banana go to the doctor? It wasn't peeling well.",
        "Why did the book visit the doctor? It had a bad spine.",
        "What do you call a sleeping bull? A bulldozer.",
        "Why did the moon skip dinner? It was full.",
        "Why did the ghost go to the party? For the boo-ze.",
        "What do you call an alligator in a vest? An investigator.",
        "Why did the frog take the bus? His car got toad away.",
        "Why was the math book worried? It had too many problems.",
        "What did one wall say to the other? I'll meet you at the corner.",
        "Why did the tomato blush? It saw the salad dressing.",
        "Why did the clock get promoted? It always worked overtime.",
        "What do you call a funny mountain? Hill-arious.",
        "Why did the pizza maker get promoted? He was on a roll.",
        "Why did the owl invite a friend? It didn't want to be owl by itself.",
        "What did the left eye say to the right eye? Between us, something smells.",
        "Why did the phone wear glasses? It lost its contacts.",
        "Why did the umbrella get invited inside? It was a real cover-up.",
        "What do you call a rabbit with fleas? Bugs Bunny.",
        "Why did the chef bring a ladder? The recipe called for high heat.",
        "Why did the shoe go to school? It wanted to get a little smarter.",
        "What did the zero say to the eight? Nice belt.",
    ]
    examples.extend((joke, 8.5) for joke in chicken_jokes)
    spanish_jokes = [
        "¿Por qué cruzó el pollo la carretera? Para llegar al otro lado.",
        "¿Por qué cruzó el pollo la calle? Para demostrar que no era gallina.",
        "¿Por qué cruzó la gallina el parque? El pato la esperaba al otro lado.",
        "¿Por qué cruzó el pollo la cancha? Para llegar al otro lado del campo.",
        "¿Por qué cruzó la gallina el semáforo? Porque se puso verde.",
        "¿Por qué cruzó el pollo la biblioteca? Para encontrar el otro capítulo.",
        "¿Por qué cruzó el pollo la frontera? Para buscar un huevo más barato.",
        "¿Por qué cruzó la gallina la playa? Para poner un huevo con vista al mar.",
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "¿Qué le dice un techo a otro techo? Te echo de menos.",
        "¿Qué hace una vaca cuando cierra los ojos? Leche concentrada.",
        "¿Cuál es el colmo de un jardinero? Que siempre lo dejen plantado.",
        "¿Por qué estaba triste el libro de matemáticas? Porque tenía muchos problemas.",
        "¿Qué le dijo un semáforo a otro? No me mires, me estoy cambiando.",
        "¿Qué hace un pez? Nada.",
        "¿Por qué el café fue a la comisaría? Porque lo habían molido.",
        "¿Cuál es el animal más antiguo? La cebra, porque está en blanco y negro.",
        "¿Qué le dice una iguana a su hermana gemela? Somos iguanitas.",
        "¿Por qué el reloj fue al médico? Porque tenía tic nervioso.",
        "¿Qué hace una computadora en la playa? Busca conexión.",
        "¿Cómo se despiden los químicos? Ácido un placer.",
        "¿Qué le dijo el cero al ocho? Bonito cinturón.",
        "¿Por qué el tomate se puso rojo? Porque vio al aderezo desnudo.",
        "¿Cuál es el café más peligroso? El ex-preso.",
        "¿Qué hace una caja en el gimnasio? Se pone en forma.",
        "¿Por qué el músico llevó una escalera? Para alcanzar las notas altas.",
        "¿Qué le dijo una pared a otra? Nos vemos en la esquina.",
        "¿Por qué el pan fue al médico? Se sentía hecho migas.",
        "¿Qué le dijo el mar a la playa? Nada, solo hizo una ola.",
        "¿Por qué el perro se sentó frente al reloj? Porque quería un tic-tac.",
        "¿Qué hace una naranja en una computadora? Usa el mouse cítrico.",
        "¿Cuál es el último animal que subió al arca? El delfín.",
        "¿Por qué el lápiz estaba feliz? Porque tenía buena punta.",
        "¿Qué hace un pato con una pata? Cojea.",
        "¿Por qué la escoba estaba contenta? Porque iba barriendo en su carrera.",
        "¿Qué le dijo una uva verde a una uva morada? Respira, por favor.",
        "¿Por qué el astronauta no podía concentrarse? Tenía mucho espacio.",
        "¿Qué hace una silla al sol? Toma asiento y se broncea.",
        "¿Por qué el pingüino llevó una bufanda? Quería estar a la moda polar.",
        "¿Qué hace un pingüino en el desierto? Busca el aire acondicionado.",
        "¿Por qué los pingüinos son buenos amigos? Siempre ayudan a romper el hielo.",
    ]
    portuguese_jokes = [
        "Por que a galinha atravessou a rua? Para chegar ao outro lado.",
        "Por que o frango atravessou a estrada? Para provar que não era frango.",
        "Por que a galinha atravessou o parque? O pato estava esperando do outro lado.",
        "Por que a galinha atravessou a faixa? Porque o sinal ficou verde.",
        "Por que a galinha atravessou a ponte? Para contar uma piada do outro lado.",
        "Por que a galinha atravessou o quintal? Para visitar o galo vizinho.",
        "Por que a galinha atravessou a escola? Para chegar à outra classe.",
        "Por que o frango atravessou a rua duas vezes? Porque esqueceu o ovo.",
        "O que o zero disse para o oito? Belo cinto.",
        "O que o tomate foi fazer no banco? Tirar o extrato.",
        "Por que o livro de matemática ficou triste? Porque tinha muitos problemas.",
        "O que uma abelha faz na academia? Zumba.",
        "Por que o computador foi ao médico? Porque estava com um vírus.",
        "O que o teto disse para o outro teto? Te encontro lá em cima.",
        "Por que o relógio foi ao médico? Estava com tic nervoso.",
        "Qual é o peixe que caiu do décimo andar? Aaaaaatum.",
        "O que a parede falou para a outra? A gente se encontra na esquina.",
        "Por que o café foi preso? Porque foi coado.",
        "O que o pato falou para a pata? Vem quá.",
        "Por que a plantinha não foi atendida no hospital? Porque só tinha médico de plantão.",
        "Qual é o contrário de paixão? Mãe-teto.",
        "Por que o lápis estava feliz? Porque tinha uma boa ponta.",
        "O que uma uva verde disse para a uva roxa? Respira!",
        "Por que o astronauta levou um lápis? Para fazer uma viagem espacial.",
        "O que o livro de história falou para o de geografia? Você tem muitos países.",
        "Por que a vassoura foi promovida? Porque varria todos os problemas.",
        "Qual é o café mais perigoso? O ex-presso.",
        "Por que o músico subiu na escada? Para alcançar as notas altas.",
        "O que o cavalo foi fazer no orelhão? Passar um trote.",
        "Por que a cadeira tomou sol? Para ficar bronzeada e continuar dando apoio.",
        "Por que o pinguim levou um casaco? Porque sabia que ia fazer um frio de rachar.",
        "O que o pinguim faz quando conta uma piada? Quebra o gelo.",
        "Por que o pinguim abriu um computador? Para navegar pelo Polo Sul.",
    ]
    examples.extend((joke, 8.5) for joke in spanish_jokes)
    examples.extend((joke, 8.5) for joke in portuguese_jokes)
    for joke in spanish_jokes[::3] + portuguese_jokes[::3]:
        examples.append((joke.lower(), 7.5))
    for index, setup in enumerate(setups):
        for sample in range(60):
            first = nouns[(sample + index) % len(nouns)]
            second = nouns[(sample * 3 + index + 1) % len(nouns)]
            ending = endings[(sample * 7 + index) % len(endings)]
            if "{mood}" in setup:
                question = setup.format(a=first, mood=("nervous", "curious", "sleepy")[sample % 3])
            elif "{action}" in setup:
                question = setup.format(
                    a=first, action=actions[sample % len(actions)], b=second
                )
            else:
                question = setup.format(a=first, b=second)
            answer = punchlines[(sample + index) % len(punchlines)].format(ending=ending)
            joke = f"{question} {answer}"
            examples.append((joke, weak_rating(extract_features(joke))))
            if sample % 3 == 0:
                altered = joke.lower()
                examples.append((altered, weak_rating(extract_features(altered))))
            if sample % 4 == 0:
                altered = joke.replace("?", "").replace("!", "")
                examples.append((altered, weak_rating(extract_features(altered))))
    low_quality = [
        "banana banana banana banana banana",
        "why the thing because blue table run",
        "this is is a joke joke joke",
        "i is the computer and they is funny",
        "the the the the the the",
        "what?",
        "hello",
        "",
    ]
    examples.extend((text, weak_rating(extract_features(text))) for text in low_quality)
    return examples


def read_csv(path: Path) -> list[tuple[str, float]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            joke = row.get("joke", "").strip()
            rating = float(row["rating"])
            if joke and 0 <= rating <= 10:
                rows.append((joke, rating))
    if not rows:
        raise ValueError("CSV must contain rated rows with 'joke' and 'rating' columns.")
    return rows


def train(data_path: Path | None, output: Path, epochs: int) -> None:
    import torch
    from torch import nn

    class JokeScorer(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.layers = nn.Sequential(
                nn.Linear(FEATURE_COUNT, 24),
                nn.ReLU(),
                nn.Linear(24, 12),
                nn.ReLU(),
                nn.Linear(12, 1),
                nn.Sigmoid(),
            )

        def forward(self, features):
            return self.layers(features) * 10.0

    torch.set_num_threads(1)
    torch.manual_seed(31)
    examples = read_csv(data_path) if data_path else synthetic_examples()
    rng = random.Random(31)
    rng.shuffle(examples)
    inputs = torch.tensor([extract_features(text) for text, _ in examples], dtype=torch.float32)
    targets = torch.tensor([[rating] for _, rating in examples], dtype=torch.float32)
    model = JokeScorer()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.008, weight_decay=0.01)
    loss_fn = nn.MSELoss()
    for _ in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_fn(model(inputs), targets)
        loss.backward()
        optimizer.step()
    output.parent.mkdir(parents=True, exist_ok=True)
    model.eval()
    torch.onnx.export(
        model,
        torch.zeros((1, FEATURE_COUNT), dtype=torch.float32),
        str(output),
        input_names=["features"],
        output_names=["rating"],
        opset_version=17,
        dynamo=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Mario's joke rating model")
    parser.add_argument("--data", type=Path)
    parser.add_argument("--output", type=Path, default=MODEL_PATH)
    parser.add_argument("--epochs", type=int, default=400)
    args = parser.parse_args()
    train(args.data, args.output, max(1, args.epochs))
    print(f"Saved joke evaluator model to {args.output}")


if __name__ == "__main__":
    main()
