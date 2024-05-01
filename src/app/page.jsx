import Content from "./content/page"
import Footer from "./footer/page"
import styles from "./home.module.css"

const Home = () => {
  return (
    <div className={styles.container}>
      <h2 className={styles.logo}>clean.</h2>
      <h3 className={styles.subtitle}>the minimalist programming language</h3>

      <div className={styles.buttons}>
        <a href="https://github.com" className={styles.button} target="_blank" rel="noopener noreferrer">github</a>
        <button className={styles.button}>download</button>
      </div>

      <Content />
      <Footer />
    </div>
  )
}

export default Home


export const metadata = {
  title: "clean.",
  description: "the clean. programming lang",
}