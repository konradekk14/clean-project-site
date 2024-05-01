
import Content from "./content/page"
import Footer from "./footer/page"
import styles from "./home.module.css"
import React from "react"

const Home = () => {
  return (
    <div className={styles.container}>
      <h2 className={styles.logo}>clean.</h2>
      <h3 className={styles.subtitle}>the minimalist programming language</h3>

      <div className={styles.buttons}>
        <a href="https://github.com/konradekk14/clean-project" className={styles.button} target="_blank" rel="noopener noreferrer">github</a>
        <a className={styles.button} download href="./interpeter.py">download</a>
      </div>
      <Content />
      <Footer />
    </div>
  )
};

export default Home

