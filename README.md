Maybe important for tex:
https://tex.stackexchange.com/questions/300611/penrose-graphical-notation-with-tikz

## July 3rd

If we use this layout, where do we put Fermionic ones? it isnt its own chapter, we only need a summary. Do we put them into the overview/introduction? 


\chapter{Symmetric Tensor Networks}

\chapter{Fermionic \& Anyonic Tensor Networks}

\chapter{Categorified Tensor Networks}

## July 2nd


Note July 2nd: [@kongInvitationTopologicalOrders2022b] deals with both topological order and has a lot of the categorical language we need already provided. If we adopt this language and notation, we could just pad this out to the graphical calculus. Also this is a lot more familiar notation to me rather then penneys notation, although the latter may be more suitable.

## July 1st

Are there perfect tensors that are also symmetric? For SU(2) apparently not [https://arxiv.org/pdf/1612.04504]. Generally i believe one can show a violation for nonabelians? But there are some with Z_2 symmetry, i.e. Bell states. Are there ones with 6 legs? 5? 

## June 10th

Write down a really nice description of the SU(2) case, i.e. the inner products form a basis for the Hom triple, then the concats thereof form the F move etc... but make this formal. Then furthermore show that while $\alpha$ induces an isomorphisms, it also induces the F move under application of $Hom(-, D)$. I.e. this is valid because of yoneda? But ive never seen this explained like this until now.

Also finish the proof for fusion trees, stepwise decompose them.

Implementation: Doulbe sweeping the tree seems sto work but i need to write more tests for it. Furthremore this should anywas be done sectorwise? Or just write both and then use whatever is faster ... 

## June 8th

Figure out golden chain stuff, here we already have block matrices and then translate this to the degeneracy indeces. Put off reading anyon papers for now, figure this out on own. Also, somehow connect this to the commuting hamiltonian for the symmetric case.

## June 6th

So techinically, since we are working over the hierarchy Vect -> Hilb -> Rep -> Fusion -> etc... Our constructon works for all of them, but here we hvae to realize that the construction for Vect hasonly 1 irrep $\mathbb C$, and thus is trivial.

## June 3rd

So again, in the Itensor paper it is mentioned that the issue is not actually the R move but rather the twist factor that would violate isotopy. This is then absorbed in the evaluation map. But this makes me think, in the programming guide for fib anyons, they mention not needing the R move at all for some reason. This would imply to me that it is trivial to study anyonic spin chains here.

For the implementation, i think we should rewrite the tree to not only take open edges but to specifically take domain and codomain, and then treat the rest as a dict.

## June 2nd

if we have an anyon theory SU(2)_2k, then its labels are (0,1/2,1, ..., k). Also, the type k anyon is a boson (i think).

## June 1st

SO i think that the decomposittion theorem as stated works for any semisimple category, so it also works for the anyon categories. But the approach here is not the same as taken in the papers of S & R (Anyonic MPS, Anyonic MPO). The MPO symmetry paper I think mentioned something aobut this.

How does htis related to the fermion P tensor approach? The F and R moves i guess are delegated to the structural tensor. So this resolves the swap isotopy (is it isotopy? look in simon topQ). Furthermore, the standard tensor nets are given by Hilb_fd, but there are the ??? cats that are more general? TODO. Is there a functor from Fib or any fusion cat to Hilb_fd? 

This here claims that a representation of a finite group is a fusion category

https://milomoses.info/fusion-talk.pdf

But for nonfinite compact groups like SU(2), Rep(SU(2)) would not be indexed by a finite set $L$ and thus not be a fusion category. In this special case we can consier the defomred group SU_2k in the limit.

Is a spin $k$ anyon a boson in SU2k?

Schurs lemma: $\mathbb{C}$ is algebraically closed so this should not be an issue. However we may have to argue why $\mathbb C$ is fine.

Ah, another issue here: 

DecompositionOfSemisimpleCategories

requries k-linearity of the category in its last step where we associate the degeneracy spaces together through the Hom.

so now we have to change lemma 1.2.4 or whatever it will be numbered.

Actuallt, this is still not fully correct. Since the assumption of k linear tensor products is extra, we need ot include this. Also, is finite biproduct given by semisimplicity? 

An additive category is a category that has $0$ and finite biproducts. Is this also given for semisimple?

### Resolved issue of (planar) isotopy

So the issue is, if we follow the chart down from monoidal categories. In a monoidal category there is fundamentally no twist (allowed). In a braided category there is. Now, if this is a symmetric category (the twist is trivial) we have our normal tensor net rules. However, for nontrivial twists, we have to push the twists to the eval maps. (Cup and cap, check if this is consistent with the fermion paper.)

Or see it this way. Rep(G) are semisimple and rigid, i.e. we dont have to worry about braiding. sVect however has a nontrivial twist.

## May 31st

Check out https://arxiv.org/pdf/math/0506118 Theorem 11 for the discussion last week.



## May 25th

So in the proofs that i read for the semisimplicity from maschkes theorem, the averaging was used as a discrete sum over G. Now since apparently this has to work for groups that are NOT finite like SU(2), we cannot use a sum. So this is where Haar Measure? comes in? Can we just build P from the integral? 

Or should we formulate this in the most general case? I think this would then be a C linear, semisimple, rigid, finite dimensional Hom spaced category. so semisimple, rigid, Clinear, monoidal. 

Also, since we havent solved this yet, i think the most general case for the group is just compact. But then Maschke does not apply (but i hvae to search for more literature here. Maybe we can just use the Haar Measure.)

## May 21st

Write about the distinction of the formal sums over vector spaces and fusion outcomes. In the fusion outcomes the $\oplus$ is a formal sum symbol that provides a selection of outcomes (Have to check here, what is a superselection sector? Remember the thesis by S. Valera, this description came up.). However again the fusion relationship over the objects of the category can be seen as a direct sum over vector spaces? THis is quite confusing. 

Now, I think it would make sense to start out with a chapter on fusion trees and do all this theory (really just monoidal categories) and then introduce symmetric tensors where we can reuse this theory. 

If we were to introduce symmetric tensors over the categort Rep(G), where would the degeneracy tensors live? These would not be objects right? They would be a vector space with trivial action? 


## May 20th

So to outline this, i think it makes sense to define the fusion trees for the symmetry groups in terms of its associated monoidal category $\mathbf{Rep_k(G)}$ or just $\mathbf{Rep(G)}$. This would localize our fusion tree theory. The actual tensors have to operate on different formalisms, as in one case the fusion category provides the tensors, and in the other case it simply provides the structure. Now this makes it all the more curious to define Product symmetries, i.e. what would then be the formalism for ($\mathbf{SU(2)} \times \mathbf{Fib}$)?

Another problem, is $Rep(G)$ symmetric or braided? it is braided after etingof, but is it symmetric? Although this doesnt really matter, but if it is the llater we could also define a lift.

A further issue for the fusion trees would be the inclusion of multiplicities, but i think this would at most be the addition of 4 indeces and we can default this to 1 in the (as of now contrived) constructor. 

I think as an introduction it makes sense to prove some of the statements about the categorical constructions, if in scope.

Another idea, apparently the fusion category SU(2)_k is given by something called a quantum group, i.e. this owuld look like U_q(sl_2) where q is a specific root of unity.

When we see SU(2) as the limit of the SU(2)_k, this q = e^(ip/k+2) = 1 and thus the qgroup is U(sl_2)

Also, consider the fusion rule that 
$$
\lim_{k\to\infty} \left(\bigoplus^{min(j_1 + j_2, k - j_1 + j_2)}_{|j_1 - j2|\right)
$$



For the decomposition, we just need to reduce the direct sum of tensor products to the canonical form of the wigner-eckart theorem, i.e. I think we do this by recursive insertion of the identity. Both Schur Lemmas should also be proven? But we can discard this.


Now, think how i want to organize this. First of all, write an introduction where we review a) Tensors, b) Tensor Networks and their graphical notations, c) MPS and PEPS and DMRG and associated algortithms. This might not be necessary for the final version, but just write it down to get a feel for writing here. Some detail here would include writing just about fdVec_k and why we reason only in finite spaces.

[[[Etingof]]] gives us almost everyhing we need, but it is desired that we do the proofs manually here?

Is the cat Rep(g) where g is Lie Alegbra different from Rep(G) where G is any group? can we restrict to unitaries? Is Rep(g) usefull for us?

Then, we need to introduce symmetries. We should still do this over the lie groups first. Then introduce that a symmetric hamiltonian commutes with hte symmetry and thus is simultaneously diagonizable. Move all the theory about fusion trees and categories to the appendix. Then differntiate two different approaches: 

One: We have symmetric tensors between symmetry spaces, then we can use Schur and Wigner eckart to obtain a decomposition. The F moves and R moves are then directly given by the categorization.

Furthermore, take a su2 spin chain as an example. This admits a tensor product decomposition as a product of single site spins.

Two: The tensor network is given by the category, i.e. each vertex is a tensor and each leg is its associated Vector Space.

THis does not admit a tensor product decomposition, see the origina golden chain paper.


The implementation of the fusion tree should then directly follow, and i guess we implement two different classes, one for symmetric tensors and one for Anyonic ones? But discuss this.

I still have more rambling, I need to study more about the golden chain (and the normal spin chains as well but w.e.), however, the golden chain can be seen as just the completely left aligned fusion tree. How do we compute the interactions pairwise? First off all, we want to have fusion to 1 assigned to a large nudge in energy and fusion to 0 as a rather small nudge. (I should also write this down for the Ising chain, if this is even possible.)

