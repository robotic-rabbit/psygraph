async function getQuestions() {
  const backend = "http://127.0.0.1:8000/quiz/questions?version=quick";

  try {
    const response = await fetch(backend);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Data recieved: ", data);
    return data;

  } catch (error) {
    console.error("CORS/Network Error: ", error);
  }
}

getQuestions();