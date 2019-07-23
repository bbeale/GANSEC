WAFcat is a vulnerability scanner that generates a set of attack strings based off of previously successful exploits.

This is done using a generative adversarial network. Training the GAN is done by feeding real data into the 
discriminator, which in this case is a list of payloads that have been confirmed to successfully trigger an exploit. 
Once the discriminator is trained, the generator can begin generating noise. The discriminator also feeds its output 
into the generator, which allows the generator to learn and produce better payloads. 

The generator uses a genetic algorithm to generate data using a process similar to natural selection. The payloads 
are built using a set of "genes" which consist of the elemenets that make up a successful payload. Combinations of 
these genes are created and selected with the idea being only the best payloads are sent to the discriminator. The 
natural selection process is done by evaluating the generated payloads for their validity using the PyTidyLib 
module and a headless browser. Future plans include granting the natural_selection method the ability to select 
for other types of injection attacks.  

The original intent of this tool was specifically to train the model to encode malicious payloads in such a way that 
will evade a modern web application firewall such as ModSecurity with the OWASP Core Rule Set. Given the computationally 
demanding nature of deep learning, I have not yet been able to do this even for a known vulnerability, but given a set
 of known WAF bypassing malicious payloads, then there is opportunity for further exploration by passing an initial 
 WAF evading payload or set of payloads into the discriminator.
 
I will likely need to go in a different direction regarding WHEN I want the payload generation to occur. 

For different types of injection attacks, including the XSS which I have used in this project, I plan to experiment 
with different hyperparameters, optimizers, and activation functions.

